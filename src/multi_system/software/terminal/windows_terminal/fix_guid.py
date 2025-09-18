from pathlib import Path
import json
import uuid
from typing import Dict, List, Any, Set

from multi_system.software.terminal.windows_terminal.path import (
    get_windows_terminal_settings_path,
)


def analyze_windows_terminal_config(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """分析Windows Terminal配置文件的格式问题"""
    issues = {
        "duplicate_guids": [],
        "missing_guids": [],
        "duplicate_profiles": [],
        "other_issues": [],
    }

    profiles = data.get("profiles", {}).get("list", [])
    if not profiles:
        return issues

    # 检查重复GUID
    guid_set = set()
    for profile in profiles:
        guid = profile.get("guid")
        if guid:
            if guid in guid_set:
                issues["duplicate_guids"].append(guid)
            else:
                guid_set.add(guid)

    # 检查缺失GUID
    for i, profile in enumerate(profiles):
        if "guid" not in profile:
            profile_name = profile.get("name", f"Unnamed profile at index {i}")
            issues["missing_guids"].append(profile_name)

    # 检查重复profile定义（基于name和commandline）
    profile_signatures = set()
    for profile in profiles:
        signature = f"{profile.get('name', '')}:{profile.get('commandline', '')}"
        if signature in profile_signatures:
            issues["duplicate_profiles"].append(signature)
        else:
            profile_signatures.add(signature)

    return issues


def fix_windows_terminal_config(
    try_to_fix: bool = True, settings_path: str = None
) -> bool:
    """修复Windows Terminal配置文件的各种问题"""
    json_path = settings_path or get_windows_terminal_settings_path()
    if not json_path or not Path(json_path).exists():
        print("Windows Terminal settings.json not found.")
        return False

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to load settings.json: {e}")
        return False

    if not data:
        print("Failed to load settings.json.")
        return False

    profiles = data.get("profiles", {}).get("list", [])
    if not profiles:
        print("No profiles found in settings.json.")
        return False

    # 分析问题
    issues = analyze_windows_terminal_config(data)

    print("=== Windows Terminal配置分析报告 ===")
    print(f"重复GUID: {len(issues['duplicate_guids'])} 个")
    print(f"缺失GUID: {len(issues['missing_guids'])} 个")
    print(f"重复profile定义: {len(issues['duplicate_profiles'])} 个")

    if issues["duplicate_guids"]:
        print(f"重复的GUID: {issues['duplicate_guids']}")

    if issues["missing_guids"]:
        print(f"缺失GUID的profile: {issues['missing_guids']}")

    if issues["duplicate_profiles"]:
        print(f"重复的profile定义: {issues['duplicate_profiles']}")

    # 如果没有问题，直接返回
    if not any(issues.values()):
        print("配置文件格式正确，无需修复。")
        return True

    # 如果需要修复
    if try_to_fix:
        print("\n=== 开始修复 ===")
        modified = False

        # 修复重复GUID - 保留第一个，修改后面的重复项
        if issues["duplicate_guids"]:
            seen_guids = set()
            for profile in profiles:
                guid = profile.get("guid")
                if guid and guid in issues["duplicate_guids"]:
                    if guid in seen_guids:
                        # 这是重复的GUID，需要修改
                        new_guid = "{" + str(uuid.uuid4()) + "}"
                        print(f"修复重复GUID: {guid} -> {new_guid}")
                        profile["guid"] = new_guid
                        modified = True
                    else:
                        # 第一次见到这个GUID，保留它
                        seen_guids.add(guid)

        # 修复缺失GUID
        if issues["missing_guids"]:
            for profile in profiles:
                if "guid" not in profile:
                    new_guid = "{" + str(uuid.uuid4()) + "}"
                    profile_name = profile.get("name", "Unnamed profile")
                    print(f"为profile '{profile_name}' 添加GUID: {new_guid}")
                    profile["guid"] = new_guid
                    modified = True

        if modified:
            # 保存修复后的配置
            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print("配置文件已成功修复并保存。")
                return True
            except Exception as e:
                print(f"保存配置文件失败: {e}")
                return False
        else:
            print("无需修复。")
            return True
    else:
        print("\n启用修复模式以自动修复这些问题。")
        return False


def validate_windows_terminal_config(settings_path: str = None) -> bool:
    """验证Windows Terminal配置文件格式"""
    json_path = settings_path or get_windows_terminal_settings_path()
    if not json_path or not Path(json_path).exists():
        print("Windows Terminal settings.json not found.")
        return False

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to load settings.json: {e}")
        return False

    issues = analyze_windows_terminal_config(data)
    has_issues = any(issues.values())

    if not has_issues:
        print("配置文件格式验证通过！")
        return True
    else:
        print("配置文件存在以下问题：")
        for issue_type, issue_list in issues.items():
            if issue_list:
                print(f"\n- {issue_type}: {len(issue_list)} 个问题")
                for issue in issue_list:
                    print(f"  * {issue}")
        return False


def main():
    """主函数：提供修复和验证选项"""
    import argparse

    parser = argparse.ArgumentParser(description="Windows Terminal配置文件修复工具")
    parser.add_argument("--fix", action="store_true", help="自动修复配置文件问题")
    parser.add_argument("--validate", action="store_true", help="仅验证配置文件格式")
    parser.add_argument("--path", help="指定配置文件路径")

    args = parser.parse_args()

    if args.validate:
        validate_windows_terminal_config(args.path)
    else:
        fix_windows_terminal_config(args.fix, args.path)


if __name__ == "__main__":
    main()
