"""
Tab: 应用启动器
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.program.packages.app_launcher import AppLauncher


class AppLauncherTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._all_apps = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Search ---
        top = QHBoxLayout()
        top.addWidget(QLabel("搜索:"))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("应用名...")
        self._search_edit.textChanged.connect(self._on_search)
        top.addWidget(self._search_edit)
        self._launch_btn = QPushButton("启动")
        self._launch_btn.clicked.connect(self._launch_selected)
        top.addWidget(self._launch_btn)
        layout.addLayout(top)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        layout.addWidget(toolbar)

        # --- Table ---
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["应用名", "命令"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

        # --- Status ---
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._refresh()

    def _force_refresh(self):
        self._refresh()

    def _refresh(self):
        self._all_apps = AppLauncher.list_apps()
        self._show_apps(self._all_apps)
        self._status_label.setText(f"共 {len(self._all_apps)} 个应用")

    def _on_search(self, keyword: str):
        if not keyword:
            self._show_apps(self._all_apps)
            return
        kw = keyword.lower()
        filtered = [a for a in self._all_apps if kw in a.name.lower() or kw in a.command.lower()]
        self._show_apps(filtered)
        self._status_label.setText(f"匹配 {len(filtered)}/{len(self._all_apps)} 个应用")

    def _show_apps(self, apps):
        self._table.setRowCount(0)
        for a in apps:
            row = self._table.rowCount()
            self._table.insertRow(row)
            name_item = QTableWidgetItem(a.name)
            name_item.setData(Qt.ItemDataRole.UserRole, a.command)
            self._table.setItem(row, 0, name_item)
            self._table.setItem(row, 1, QTableWidgetItem(a.command))

    def _launch_selected(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "提示", "请先选择一个应用")
            return
        item = self._table.item(rows[0].row(), 0)
        command = item.data(Qt.ItemDataRole.UserRole) if item else ""
        if not command:
            return
        if AppLauncher.launch(command):
            self._status_label.setText(f"已启动: {item.text()}")
        else:
            QMessageBox.warning(self, "失败", f"无法启动: {item.text()}")
