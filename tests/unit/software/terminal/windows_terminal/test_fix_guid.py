"""
Windows Terminal GUID修复工具的单元测试
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from multi_system.software.terminal.windows_terminal.fix_guid import (
    analyze_windows_terminal_config,
    fix_windows_terminal_config,
    validate_windows_terminal_config,
)


class TestWindowsTerminalFixGuid:
    """Windows Terminal修复工具测试类"""

    def test_analyze_config_no_issues(self):
        """测试分析没有问题的配置"""
        config = {
            "profiles": {
                "list": [
                    {
                        "name": "PowerShell",
                        "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
                        "commandline": "powershell.exe",
                    },
                    {
                        "name": "CMD",
                        "guid": "{0caa0dad-35be-5f56-a8ff-afceeeaa6101}",
                        "commandline": "cmd.exe",
                    },
                ]
            }
        }

        issues = analyze_windows_terminal_config(config)

        assert not any(issues.values()), "应该没有检测到问题"

    def test_analyze_config_duplicate_guids(self):
        """测试分析重复GUID"""
        config = {
            "profiles": {
                "list": [
                    {
                        "name": "PowerShell 1",
                        "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
                        "commandline": "powershell.exe",
                    },
                    {
                        "name": "PowerShell 2",
                        "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",  # 重复GUID
                        "commandline": "powershell.exe -NoExit",
                    },
                ]
            }
        }

        issues = analyze_windows_terminal_config(config)

        assert len(issues["duplicate_guids"]) == 1
        assert "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}" in issues["duplicate_guids"]

    def test_analyze_config_missing_guids(self):
        """测试分析缺失GUID"""
        config = {
            "profiles": {
                "list": [
                    {
                        "name": "PowerShell",
                        "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
                        "commandline": "powershell.exe",
                    },
                    {
                        "name": "CMD Missing",  # 缺失GUID
                        "commandline": "cmd.exe",
                    },
                ]
            }
        }

        issues = analyze_windows_terminal_config(config)

        assert len(issues["missing_guids"]) == 1
        assert "CMD Missing" in issues["missing_guids"]

    def test_analyze_config_duplicate_profiles(self):
        """测试分析重复profile定义"""
        config = {
            "profiles": {
                "list": [
                    {
                        "name": "Git Bash",
                        "guid": "{2ece5bfe-50ed-5f3a-ab87-5cd4baafed2b}",
                        "commandline": "git-bash.exe",
                    },
                    {
                        "name": "Git Bash",  # 重复名称
                        "guid": "{abcdef12-3456-7890-abcd-ef1234567890}",
                        "commandline": "git-bash.exe",  # 重复命令行
                    },
                ]
            }
        }

        issues = analyze_windows_terminal_config(config)

        assert len(issues["duplicate_profiles"]) == 1
        assert "Git Bash:git-bash.exe" in issues["duplicate_profiles"]

    def test_fix_config_duplicate_guids(self):
        """测试修复重复GUID"""
        config = {
            "profiles": {
                "list": [
                    {
                        "name": "PowerShell 1",
                        "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
                        "commandline": "powershell.exe",
                    },
                    {
                        "name": "PowerShell 2",
                        "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",  # 重复GUID
                        "commandline": "powershell.exe -NoExit",
                    },
                ]
            }
        }

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f, indent=4)
            temp_file = f.name

        try:
            # 执行修复
            result = fix_windows_terminal_config(True, temp_file)
            assert result, "修复应该成功"

            # 读取修复后的配置
            with open(temp_file, "r") as f:
                fixed_config = json.load(f)

            profiles = fixed_config["profiles"]["list"]

            # 检查GUID格式和唯一性
            guids = [profile["guid"] for profile in profiles if "guid" in profile]
            assert len(guids) == len(set(guids)), "所有GUID应该是唯一的"

            # 检查GUID格式
            for guid in guids:
                assert guid.startswith("{") and guid.endswith("}"), (
                    f"GUID格式不正确: {guid}"
                )

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_fix_config_missing_guids(self):
        """测试修复缺失GUID"""
        config = {
            "profiles": {
                "list": [
                    {
                        "name": "PowerShell",
                        "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
                        "commandline": "powershell.exe",
                    },
                    {
                        "name": "CMD Missing",  # 缺失GUID
                        "commandline": "cmd.exe",
                    },
                ]
            }
        }

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f, indent=4)
            temp_file = f.name

        try:
            # 执行修复
            result = fix_windows_terminal_config(True, temp_file)
            assert result, "修复应该成功"

            # 读取修复后的配置
            with open(temp_file, "r") as f:
                fixed_config = json.load(f)

            profiles = fixed_config["profiles"]["list"]

            # 检查所有profile都有GUID
            for profile in profiles:
                assert "guid" in profile, "所有profile都应该有GUID"
                assert profile["guid"].startswith("{") and profile["guid"].endswith(
                    "}"
                ), f"GUID格式不正确: {profile['guid']}"

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @patch(
        "multi_system.software.terminal.windows_terminal.fix_guid.get_windows_terminal_settings_path"
    )
    def test_validate_config_file_not_found(self, mock_get_path):
        """测试验证时文件不存在的情况"""
        mock_get_path.return_value = "/nonexistent/path/settings.json"

        result = validate_windows_terminal_config()
        assert not result, "文件不存在时验证应该失败"

    @patch(
        "multi_system.software.terminal.windows_terminal.fix_guid.get_windows_terminal_settings_path"
    )
    def test_fix_config_file_not_found(self, mock_get_path):
        """测试修复时文件不存在的情况"""
        mock_get_path.return_value = "/nonexistent/path/settings.json"

        result = fix_windows_terminal_config(True)
        assert not result, "文件不存在时修复应该失败"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
