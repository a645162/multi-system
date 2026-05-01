"""
Tab: 进程管理
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.system.monitor.processes import ProcessManager


class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("搜索:"))
        self._search = QLineEdit()
        self._search.setPlaceholderText("进程名/PID...")
        self._search.textChanged.connect(self._on_search)
        top.addWidget(self._search)
        layout.addLayout(top)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addAction("结束进程", self._kill_selected)
        toolbar.addAction("强制结束", lambda: self._kill_selected(force=True))
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(["PID", "名称", "用户", "CPU%", "内存MB", "状态"])
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
        procs = ProcessManager.list_processes()
        self._show_procs(procs)

    def _on_search(self, keyword: str):
        if not keyword:
            self._refresh()
            return
        procs = ProcessManager.search(keyword)
        self._show_procs(procs)

    def _show_procs(self, procs):
        self._table.setRowCount(0)
        for p in procs[:200]:
            row = self._table.rowCount()
            self._table.insertRow(row)
            items = [
                QTableWidgetItem(str(p.pid)),
                QTableWidgetItem(p.name),
                QTableWidgetItem(p.username),
                QTableWidgetItem(f"{p.cpu_percent:.1f}"),
                QTableWidgetItem(f"{p.memory_mb:.1f}"),
                QTableWidgetItem(p.status),
            ]
            items[0].setData(Qt.ItemDataRole.UserRole, p.pid)
            for col, item in enumerate(items):
                self._table.setItem(row, col, item)

    def _kill_selected(self, force: bool = False):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        pid_item = self._table.item(rows[0].row(), 0)
        pid = pid_item.data(Qt.ItemDataRole.UserRole)
        name = self._table.item(rows[0].row(), 1).text()
        mode = "强制结束" if force else "结束"
        reply = QMessageBox.warning(
            self, f"确认{mode}",
            f"确定要{mode}进程 {name} (PID: {pid}) 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if ProcessManager.kill(pid, force):
                self._refresh()
            else:
                QMessageBox.warning(self, "失败", f"无法{mode}进程，可能需要管理员权限")
