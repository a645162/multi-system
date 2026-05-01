"""
系统监控工具箱
"""

from multi_system.gui.base_toolbox import BaseToolboxWindow
from multi_system.gui.system_tabs.dashboard_tab import DashboardTab
from multi_system.gui.system_tabs.disk_tab import DiskTab
from multi_system.gui.system_tabs.process_tab import ProcessTab
from multi_system.gui.system_tabs.startup_tab import StartupTab


class SystemToolboxWindow(BaseToolboxWindow):
    TABS = [
        (DashboardTab, "系统仪表盘"),
        (ProcessTab, "进程管理"),
        (DiskTab, "磁盘分析"),
        (StartupTab, "启动项管理"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统监控工具箱")
