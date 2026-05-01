"""
Tab: 进程管理
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
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
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("排序:"))
        self._sort_combo = QComboBox()
        self._sort_combo.addItems(["按CPU排序", "按内存排序", "按名称排序", "按PID排序"])
        self._sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        toolbar.addWidget(self._sort_combo)
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(["PID", "名称", "用户", "CPU%", "内存MB", "状态"])
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

        kill_action = menu.addAction("结束进程")
        kill_action.triggered.connect(self._kill_selected)

        force_kill_action = menu.addAction("强制结束")
        force_kill_action.triggered.connect(lambda: self._kill_selected(force=True))

        menu.addSeparator()

        pid_item = self._table.item(row, 0)
        pid_text = pid_item.text() if pid_item else ""
        name_item = self._table.item(row, 1)
        name_text = name_item.text() if name_item else ""

        copy_pid_action = menu.addAction("复制 PID")
        copy_pid_action.triggered.connect(lambda: self._copy_to_clipboard(pid_text))

        copy_name_action = menu.addAction("复制进程名")
        copy_name_action.triggered.connect(lambda: self._copy_to_clipboard(name_text))

        copy_cmdline_action = menu.addAction("复制命令行")
        copy_cmdline_action.triggered.connect(lambda: self._copy_cmdline(row))

        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)

    def _copy_cmdline(self, row: int):
        pid_item = self._table.item(row, 0)
        if not pid_item:
            return
        pid = pid_item.data(Qt.ItemDataRole.UserRole)
        try:
            import psutil
            p = psutil.Process(pid)
            cmdline = " ".join(p.cmdline())
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(cmdline)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            QMessageBox.warning(self, "失败", "无法获取进程命令行")

    # --- Existing methods ---

    def _force_refresh(self):
        self._refresh()

    def _on_sort_changed(self, index: int):
        sort_map = {0: "cpu", 1: "mem", 2: "name", 3: "pid"}
        sort_by = sort_map.get(index, "cpu")
        procs = ProcessManager.list_processes(sort_by=sort_by)
        self._show_procs(procs)

    def _refresh(self):
        sort_map = {0: "cpu", 1: "mem", 2: "name", 3: "pid"}
        sort_by = sort_map.get(self._sort_combo.currentIndex(), "cpu")
        procs = ProcessManager.list_processes(sort_by=sort_by)
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
