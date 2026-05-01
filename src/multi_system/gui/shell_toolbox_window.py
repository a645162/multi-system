"""
Shell 工具箱主窗口 - 7个功能Tab
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMainWindow, QTabWidget

from multi_system.gui.shell_tabs.alias_tab import AliasTab
from multi_system.gui.shell_tabs.completions_tab import CompletionsTab
from multi_system.gui.shell_tabs.history_tab import HistoryTab
from multi_system.gui.shell_tabs.migration_tab import MigrationTab
from multi_system.gui.shell_tabs.prompt_tab import PromptTab
from multi_system.gui.shell_tabs.rc_manager_tab import RCManagerTab
from multi_system.gui.shell_tabs.startup_tab import StartupTab


class ShellToolboxWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shell 工具箱")
        self.setMinimumSize(QSize(800, 550))

        tabs = QTabWidget()
        tabs.addTab(RCManagerTab(), "RC 配置管理")
        tabs.addTab(HistoryTab(), "历史分析")
        tabs.addTab(AliasTab(), "Alias 管理")
        tabs.addTab(PromptTab(), "Prompt 主题")
        tabs.addTab(CompletionsTab(), "补全管理")
        tabs.addTab(MigrationTab(), "配置迁移")
        tabs.addTab(StartupTab(), "启动分析")

        self.setCentralWidget(tabs)
