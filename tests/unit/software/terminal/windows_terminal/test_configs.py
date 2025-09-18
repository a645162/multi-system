"""
Windows Terminal测试配置文件
包含各种测试场景的配置数据
"""

# 正常配置 - 没有问题的配置
VALID_CONFIG = {
    "profiles": {
        "list": [
            {
                "name": "Windows PowerShell",
                "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
                "commandline": "%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                "hidden": False,
            },
            {
                "name": "命令提示符",
                "guid": "{0caa0dad-35be-5f56-a8ff-afceeeaa6101}",
                "commandline": "%SystemRoot%\\System32\\cmd.exe",
                "hidden": False,
            },
        ]
    }
}

# 包含重复GUID的配置
DUPLICATE_GUID_CONFIG = {
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
            {
                "name": "PowerShell 3",
                "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",  # 重复GUID
                "commandline": "powershell.exe -ExecutionPolicy Bypass",
            },
        ]
    }
}

# 包含缺失GUID的配置
MISSING_GUID_CONFIG = {
    "profiles": {
        "list": [
            {
                "name": "PowerShell",
                "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
                "commandline": "powershell.exe",
            },
            {
                "name": "Anaconda Prompt",  # 缺失GUID
                "commandline": "cmd.exe /K activate.bat",
            },
            {
                "name": "Custom Shell",  # 缺失GUID
                "commandline": "bash.exe",
            },
        ]
    }
}

# 包含重复profile定义的配置
DUPLICATE_PROFILE_CONFIG = {
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
            {
                "name": "Ubuntu",
                "guid": "{2c4de342-38b7-51cf-b940-2309a097f518}",
                "source": "Windows.Terminal.Wsl",
            },
            {
                "name": "Ubuntu",  # 重复名称，但source不同
                "guid": "{51855cb2-8cce-5362-8f54-464b92b32386}",
                "source": "CanonicalGroupLimited.Ubuntu_79rhkp1fndgsc",
            },
        ]
    }
}

# 混合问题的配置（重复GUID + 缺失GUID）
MIXED_ISSUES_CONFIG = {
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
            {
                "name": "Anaconda Prompt",  # 缺失GUID
                "commandline": "cmd.exe /K activate.bat",
            },
            {
                "name": "Git Bash",
                "guid": "{2ece5bfe-50ed-5f3a-ab87-5cd4baafed2b}",
                "commandline": "git-bash.exe",
            },
            {
                "name": "Git Bash",  # 重复profile
                "guid": "{abcdef12-3456-7890-abcd-ef1234567890}",
                "commandline": "git-bash.exe",  # 重复命令行
            },
        ]
    }
}

# 复杂的真实配置示例（基于用户提供的配置）
REAL_WORLD_CONFIG = {
    "$help": "https://aka.ms/terminal-documentation",
    "$schema": "https://aka.ms/terminal-profiles-schema",
    "defaultProfile": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
    "profiles": {
        "defaults": {},
        "list": [
            {
                "commandline": "%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
                "hidden": False,
                "name": "Windows PowerShell",
            },
            {
                "commandline": "%SystemRoot%\\System32\\cmd.exe",
                "guid": "{0caa0dad-35be-5f56-a8ff-afceeeaa6101}",
                "hidden": False,
                "name": "命令提示符",
            },
            {
                "commandline": "%WINDIR%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -ExecutionPolicy ByPass -NoExit -Command \"& 'C:\\Users\\user\\miniconda3\\shell\\condabin\\conda-hook.ps1' ; conda activate 'C:\\Users\\user\\miniconda3' \"",
                "name": "Anaconda PowerShell Prompt (miniconda3)",  # 缺失GUID
                "icon": "C:\\Users\\user\\miniconda3\\Menu\\anaconda_powershell_prompt.ico",
                "startingDirectory": "C:\\Users\\user",
            },
            {
                "commandline": '%WINDIR%\\System32\\cmd.exe "/K" C:\\Users\\user\\miniconda3\\Scripts\\activate.bat C:\\Users\\user\\miniconda3',
                "name": "Anaconda Prompt (miniconda3)",  # 缺失GUID
                "icon": "C:\\Users\\user\\miniconda3\\Menu\\anaconda_prompt.ico",
                "startingDirectory": "C:\\Users\\user",
            },
        ],
    },
}
