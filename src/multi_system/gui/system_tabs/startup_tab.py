"""
Tab: 启动项管理
"""

from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.system.monitor.startup_apps import StartupAppManager


class StartupTab(QWidget):
    def __init__(self):
        super().__init__()
        self._manager = StartupAppManager()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["名称", "命令", "来源", "启用"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._refresh()

    def _force_refresh(self):
        self._refresh()

    def _refresh(self):
        apps = self._manager.list_apps()
        self._table.setRowCount(0)
        for app in apps:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(app.name))
            self._table.setItem(row, 1, QTableWidgetItem(app.command[:120]))
            self._table.setItem(row, 2, QTableWidgetItem(app.source))
            self._table.setItem(row, 3, QTableWidgetItem("✓" if app.enabled else "✗"))
