from multi_system.gui.base_toolbox import BaseToolboxWindow
from multi_system.gui.package_tabs.app_launcher_tab import AppLauncherTab
from multi_system.gui.package_tabs.package_tab import PackageTab


class PackageToolboxWindow(BaseToolboxWindow):
    TABS = [
        (PackageTab, "包管理器"),
        (AppLauncherTab, "应用启动器"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("软件管理")
