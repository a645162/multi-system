"""
GUI主窗口 - 功能选择器
从 registry 读取所有已注册功能
"""

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QWidget,
)

from multi_system.gui.registry import get_all


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-System 工具箱")
        self.setMinimumSize(QSize(500, 400))
        self._sub_windows: list = []
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        layout = QHBoxLayout(central)

        self._list = QListWidget()
        self._list.setIconSize(QSize(48, 48))
        self._list.setSpacing(8)
        self._list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._list.setFocus()

        for feat in get_all():
            item = QListWidgetItem(feat.name)
            item.setData(Qt.ItemDataRole.UserRole, feat.id)
            item.setToolTip(feat.description)
            self._list.addItem(item)

        layout.addWidget(self._list)
        self.setCentralWidget(central)

        self.statusBar().showMessage("双击或按 Enter 启动功能")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._launch_selected()
        else:
            super().keyPressEvent(event)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        self._launch_feature(item.data(Qt.ItemDataRole.UserRole))

    def _launch_selected(self):
        item = self._list.currentItem()
        if item:
            self._launch_feature(item.data(Qt.ItemDataRole.UserRole))

    def _launch_feature(self, feature_id: str):
        from multi_system.gui.registry import get_by_id
        feat = get_by_id(feature_id)
        if feat is None or feat.window_factory is None:
            return
        win = feat.window_factory()
        self._sub_windows.append(win)
        win.show()
