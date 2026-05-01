# Multi-System

跨平台系统管理工具箱，支持 Python API / CLI / GUI 三种入口。

## 入口

- **CLI**: `multi-system <command>` — 命令行入口
- **GUI**: `multi-system-gui [command]` — 图形界面入口，无参数显示功能选择器

## 9 个功能模块

| CLI 命令 | 工具箱 | Tab 数 |
|----------|--------|--------|
| `port-forward` | 端口转发 | 1 (独立窗口) |
| `shell-toolbox` | Shell 工具箱 | 7 |
| `system-monitor` | 系统监控 | 4 |
| `network-toolbox` | 网络工具箱 | 4 |
| `dev-toolbox` | 开发工具箱 | 4 |
| `file-toolbox` | 文件工具箱 | 4 |
| `package-toolbox` | 软件管理 | 2 |
| `security-toolbox` | 安全工具箱 | 3 |
| `ai-toolbox` | AI 模型切换 | 2 |

## 架构

```
src/multi_system/
  main.py              # CLI 入口，registry 分发
  main_gui.py          # GUI 入口
  core/
    data_manager.py    # TOML/YAML 读写 (tomli_w, pyyaml)
  path/
    paths.py           # 跨平台路径工具
  gui/
    registry.py        # 功能注册中心 — 新功能只需 register()
    base_toolbox.py    # BaseToolboxWindow — 子类定义 TABS 列表即可
    main_window.py     # 功能选择器
    *_toolbox_window.py  # 各工具箱窗口
    *_tabs/            # 各工具箱的 Tab 页
  network/             # 端口转发、DNS、代理、网速、端口扫描、NTP
  system/
    monitor/           # 仪表盘、进程、磁盘、启动项 (psutil)
    security/          # 防火墙、文件权限审计
    shells/            # RC管理、历史、Alias、Prompt、补全、迁移、启动分析
    envs.py, fonts.py, machine.py, windows/uac.py
  program/
    env_var_manager.py, ssh_keys.py, cron_manager.py, log_viewer.py
    packages/          # 包管理器封装、应用启动器
    ai_models/         # AI模型配置/切换 (Claude Code, Codex, OpenCode, OpenClaw, Hermes)
  files/               # 大文件、重复文件、批量重命名、文件监控、软连接
  software/            # Windows Terminal 工具
```

## 关键模式

- **新增功能**: 在 `gui/registry.py` 调用 `register(FeatureInfo(...))`，CLI/GUI/主窗口自动获取
- **工具箱窗口**: 继承 `BaseToolboxWindow`，定义 `TABS = [(TabClass, "标签名"), ...]`
- **Tab 懒加载**: `showEvent` + `_loaded` 标志，首次切入自动刷新
- **数据持久化**: `DataManager` 读写 TOML/YAML，数据存 `./data/{feature}/`
- **端口转发**: `PortForwardEngine` 纯 asyncio，`PortForwardWorker` (QThread) 桥接 Qt

## 开发

```bash
# 安装
pip install -e ".[gui]"

# 检查
ruff check src/multi_system/
ty check  # 或 find src/multi_system -name "*.py" | xargs ty check

# 测试
multi-system --help
multi-system-gui
```

## 技术栈

- Python 3.13+，PySide6 (Qt6)
- psutil, requests, beautifulsoup4, tomli_w, pyyaml
- Lint: ruff + ty
