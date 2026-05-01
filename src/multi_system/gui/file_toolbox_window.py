from multi_system.gui.base_toolbox import BaseToolboxWindow
from multi_system.gui.file_tabs.big_file_tab import BigFileTab
from multi_system.gui.file_tabs.duplicate_tab import DuplicateTab
from multi_system.gui.file_tabs.rename_tab import RenameTab
from multi_system.gui.file_tabs.watcher_tab import WatcherTab


class FileToolboxWindow(BaseToolboxWindow):
    TABS = [
        (BigFileTab, "大文件查找"),
        (DuplicateTab, "重复文件"),
        (RenameTab, "批量重命名"),
        (WatcherTab, "文件监控"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件工具箱")
