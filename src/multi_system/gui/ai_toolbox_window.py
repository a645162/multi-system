"""
AI 模型切换工具箱
"""

from multi_system.gui.ai_tabs.profile_tab import ProfileTab
from multi_system.gui.ai_tabs.quick_switch_tab import QuickSwitchTab
from multi_system.gui.base_toolbox import BaseToolboxWindow


class AIToolboxWindow(BaseToolboxWindow):
    TABS = [
        (ProfileTab, "配置管理"),
        (QuickSwitchTab, "快捷切换"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 模型切换")
