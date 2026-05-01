"""
工具箱窗口基类
子类只需定义 TABS 列表即可
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget


class BaseToolboxWindow(QMainWindow):
    TABS: list[tuple[type[QWidget], str]] = []

    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(800, 550))

        tabs = QTabWidget()
        for tab_cls, label in self.TABS:
            tabs.addTab(tab_cls(), label)
        self.setCentralWidget(tabs)
