"""
Shell 工具箱主窗口 - 7个功能Tab
"""

from multi_system.gui.base_toolbox import BaseToolboxWindow
from multi_system.gui.shell_tabs.alias_tab import AliasTab
from multi_system.gui.shell_tabs.completions_tab import CompletionsTab
from multi_system.gui.shell_tabs.history_tab import HistoryTab
from multi_system.gui.shell_tabs.migration_tab import MigrationTab
from multi_system.gui.shell_tabs.prompt_tab import PromptTab
from multi_system.gui.shell_tabs.rc_manager_tab import RCManagerTab
from multi_system.gui.shell_tabs.startup_tab import StartupTab


class ShellToolboxWindow(BaseToolboxWindow):
    TABS = [
        (RCManagerTab, "RC 配置管理"),
        (HistoryTab, "历史分析"),
        (AliasTab, "Alias 管理"),
        (PromptTab, "Prompt 主题"),
        (CompletionsTab, "补全管理"),
        (MigrationTab, "配置迁移"),
        (StartupTab, "启动分析"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shell 工具箱")
