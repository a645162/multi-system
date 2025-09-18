# Windows Terminal 配置文件修复工具

## 功能概述

这个工具用于检测和修复 Windows Terminal 配置文件 (`settings.json`) 中的常见问题：

1. **重复的GUID** - 多个profile使用相同的GUID
2. **缺失的GUID** - profile缺少必需的GUID字段
3. **重复的profile定义** - 相同名称和命令行配置的profile

## 安装和使用

### 基本使用

```bash
# 验证配置文件格式
python -m multi_system.software.terminal.windows_terminal.fix_guid --validate

# 自动修复配置文件问题
python -m multi_system.software.terminal.windows_terminal.fix_guid --fix

# 指定自定义配置文件路径
python -m multi_system.software.terminal.windows_terminal.fix_guid --fix --path "C:\path\to\settings.json"
```

### 命令行参数

- `--validate`: 仅验证配置文件格式，不进行修改
- `--fix`: 自动修复检测到的问题
- `--path`: 指定自定义配置文件路径

## 配置文件格式要求

### 正确的GUID格式

每个profile必须有一个唯一的GUID，格式为UUID：

```json
{
    "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
    "name": "Windows PowerShell",
    "commandline": "powershell.exe"
}
```

### 常见问题示例

#### 问题1: 重复GUID
```json
{
    "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
    "name": "PowerShell 1"
},
{
    "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",  // 重复GUID
    "name": "PowerShell 2"
}
```

#### 问题2: 缺失GUID
```json
{
    "name": "Anaconda Prompt",  // 缺少guid字段
    "commandline": "cmd.exe /K activate.bat"
}
```

#### 问题3: 重复profile定义
```json
{
    "name": "Git Bash",
    "commandline": "git-bash.exe"
},
{
    "name": "Git Bash",  // 重复名称
    "commandline": "git-bash.exe"  // 重复命令行
}
```

## 修复流程

1. **检测阶段**: 分析配置文件，识别所有问题
2. **报告阶段**: 显示检测到的问题详情
3. **修复阶段** (如果启用):
   - 为重复GUID生成新的唯一GUID
   - 为缺失GUID的profile添加新GUID
   - 保留重复profile定义（需要手动处理）

## 最佳实践

1. **定期验证**: 在修改配置文件后运行验证
2. **备份配置**: 修复前建议备份原始文件
3. **手动审查**: 对于重复profile定义，需要手动决定保留哪个

## 配置文件位置

默认的 Windows Terminal 配置文件路径：
```
C:\Users\<用户名>\AppData\Local\Packages\Microsoft.WindowsTerminal_<随机字符>\LocalState\settings.json
```

## 注意事项

- 工具会自动检测并修复GUID相关问题
- 重复profile定义需要手动处理，工具只会报告而不会自动删除
- 修复操作会直接修改配置文件，建议先备份

## 开发说明

工具基于Python开发，主要功能在 `fix_guid.py` 中实现：

- `analyze_windows_terminal_config()`: 分析配置问题
- `fix_windows_terminal_config()`: 修复配置问题
- `validate_windows_terminal_config()`: 验证配置格式

支持自定义配置文件路径和灵活的修复选项。