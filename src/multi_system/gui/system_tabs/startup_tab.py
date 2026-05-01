"""
Tab: 启动项管理
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMenu,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.system.monitor.startup_apps import StartupApp, StartupAppManager


class StartupTab(QWidget):
    def __init__(self):
        super().__init__()
        self._manager = StartupAppManager()
        self._apps: list[StartupApp] = []
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addSeparator()
        toolbar.addAction("启用", self._enable_selected)
        toolbar.addAction("禁用", self._disable_selected)
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["名称", "命令", "来源", "启用"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._table)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._refresh()

    # --- Context menu ---

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)

        menu = QMenu(self)

        enabled_item = self._table.item(row, 3)
        is_enabled = enabled_item.text() == "✓" if enabled_item else False

        if is_enabled:
            toggle_action = menu.addAction("禁用")
            toggle_action.triggered.connect(self._disable_selected)
        else:
            toggle_action = menu.addAction("启用")
            toggle_action.triggered.connect(self._enable_selected)

        menu.addSeparator()

        name_item = self._table.item(row, 0)
        name_text = name_item.text() if name_item else ""
        cmd_item = self._table.item(row, 1)
        cmd_text = cmd_item.text() if cmd_item else ""

        copy_cmd_action = menu.addAction("复制命令")
        copy_cmd_action.triggered.connect(lambda: self._copy_to_clipboard(cmd_text))

        copy_name_action = menu.addAction("复制名称")
        copy_name_action.triggered.connect(lambda: self._copy_to_clipboard(name_text))

        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)

    # --- Existing methods ---

    def _force_refresh(self):
        self._refresh()

    def _refresh(self):
        self._apps = self._manager.list_apps()
        self._table.setRowCount(0)
        for app in self._apps:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(app.name))
            self._table.setItem(row, 1, QTableWidgetItem(app.command[:120]))
            self._table.setItem(row, 2, QTableWidgetItem(app.source))
            self._table.setItem(row, 3, QTableWidgetItem("✓" if app.enabled else "✗"))

    # --- New toolbar/context actions ---

    def _enable_selected(self):
        self._toggle_selected(enable=True)

    def _disable_selected(self):
        self._toggle_selected(enable=False)

    def _toggle_selected(self, enable: bool):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        if row >= len(self._apps):
            return
        app = self._apps[row]
        label = "启用" if enable else "禁用"
        reply = QMessageBox.warning(
            self,
            f"确认{label}",
            f"确定要{label}启动项 {app.name} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if StartupAppManager.toggle_autostart(app, enable):
            QMessageBox.information(self, "成功", f"{app.name} 已{label}")
            self._refresh()
        else:
            QMessageBox.warning(self, "失败", f"无法{label} {app.name}，可能不支持此操作")
