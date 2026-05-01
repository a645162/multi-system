"""
功能注册中心
新增功能只需调用 register()，主窗口/CLI/GUI入口自动获取
"""

from collections.abc import Callable
from dataclasses import dataclass

_REGISTRY: dict[str, "FeatureInfo"] = {}


@dataclass
class FeatureInfo:
    id: str
    name: str
    description: str
    cli_name: str = ""
    window_factory: Callable | None = None

    def __post_init__(self):
        if not self.cli_name:
            self.cli_name = self.id


def register(feature: FeatureInfo) -> None:
    _REGISTRY[feature.id] = feature


def get_all() -> list[FeatureInfo]:
    return list(_REGISTRY.values())


def get_by_id(fid: str) -> FeatureInfo | None:
    return _REGISTRY.get(fid)


def get_by_cli(name: str) -> FeatureInfo | None:
    for f in _REGISTRY.values():
        if f.cli_name == name:
            return f
    return None


# --- 注册已有功能 ---

register(FeatureInfo(
    id="port-forward",
    name="端口转发",
    description="TCP端口转发管理工具，支持添加、启停转发规则",
    cli_name="port-forward",
    window_factory=lambda: __import__(
        "multi_system.gui.port_forward_window", fromlist=["PortForwardWindow"]
    ).PortForwardWindow(),
))

register(FeatureInfo(
    id="shell-toolbox",
    name="Shell 工具箱",
    description="RC管理、历史分析、Alias、Prompt主题、补全、迁移、启动分析",
    cli_name="shell-toolbox",
    window_factory=lambda: __import__(
        "multi_system.gui.shell_toolbox_window", fromlist=["ShellToolboxWindow"]
    ).ShellToolboxWindow(),
))

register(FeatureInfo(
    id="system-monitor",
    name="系统监控",
    description="系统仪表盘、进程管理、磁盘分析、启动项管理",
    cli_name="system-monitor",
    window_factory=lambda: __import__(
        "multi_system.gui.system_toolbox_window", fromlist=["SystemToolboxWindow"]
    ).SystemToolboxWindow(),
))

register(FeatureInfo(
    id="network-toolbox",
    name="网络工具箱",
    description="DNS切换、代理管理、网速测试、端口扫描",
    cli_name="network-toolbox",
    window_factory=lambda: __import__(
        "multi_system.gui.network_toolbox_window", fromlist=["NetworkToolboxWindow"]
    ).NetworkToolboxWindow(),
))

register(FeatureInfo(
    id="ai-toolbox",
    name="AI 模型切换",
    description="AI模型Profile管理、快捷切换，支持Claude Code/Codex/OpenCode/OpenClaw/Hermes",
    cli_name="ai-toolbox",
    window_factory=lambda: __import__(
        "multi_system.gui.ai_toolbox_window", fromlist=["AIToolboxWindow"]
    ).AIToolboxWindow(),
))

register(FeatureInfo(
    id="dev-toolbox",
    name="开发工具箱",
    description="环境变量管理、SSH密钥、定时任务、日志查看",
    cli_name="dev-toolbox",
    window_factory=lambda: __import__(
        "multi_system.gui.dev_toolbox_window", fromlist=["DevToolboxWindow"]
    ).DevToolboxWindow(),
))

register(FeatureInfo(
    id="file-toolbox",
    name="文件工具箱",
    description="大文件查找、重复文件、批量重命名、文件监控",
    cli_name="file-toolbox",
    window_factory=lambda: __import__(
        "multi_system.gui.file_toolbox_window", fromlist=["FileToolboxWindow"]
    ).FileToolboxWindow(),
))

register(FeatureInfo(
    id="package-toolbox",
    name="软件管理",
    description="跨平台包管理器、应用启动器",
    cli_name="package-toolbox",
    window_factory=lambda: __import__(
        "multi_system.gui.package_toolbox_window", fromlist=["PackageToolboxWindow"]
    ).PackageToolboxWindow(),
))

register(FeatureInfo(
    id="security-toolbox",
    name="安全工具箱",
    description="防火墙管理、端口扫描、文件权限审计",
    cli_name="security-toolbox",
    window_factory=lambda: __import__(
        "multi_system.gui.security_toolbox_window", fromlist=["SecurityToolboxWindow"]
    ).SecurityToolboxWindow(),
))
