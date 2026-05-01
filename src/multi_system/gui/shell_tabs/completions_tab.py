"""
Tab: 补全管理
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.system.shells.completions import CompletionManager


class CompletionsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._manager: CompletionManager | None = None
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Shell:"))
        self._shell_combo = QComboBox()
        self._shell_combo.addItems(["bash", "zsh", "fish"])
        self._shell_combo.currentTextChanged.connect(self._on_shell_changed)
        top.addWidget(self._shell_combo)
        top.addStretch()
        layout.addLayout(top)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addAction("打开目录", self._open_dir)
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["补全脚本", "路径", "大小"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._on_shell_changed(self._shell_combo.currentText())

    def _on_shell_changed(self, shell: str):
        self._manager = CompletionManager(shell)
        self._refresh()

    def _force_refresh(self):
        self._on_shell_changed(self._shell_combo.currentText())

    def _refresh(self):
        if not self._manager:
            return
        entries = self._manager.list_completions()
        self._table.setRowCount(0)
        for e in entries:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(e.name))
            self._table.setItem(row, 1, QTableWidgetItem(str(e.path)))
            self._table.setItem(row, 2, QTableWidgetItem(f"{e.size} B"))

    def _open_dir(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        path = self._table.item(rows[0].row(), 1).text()
        parent = os.path.dirname(path)
        os.system(f"xdg-open '{parent}' 2>/dev/null || open '{parent}' 2>/dev/null || explorer '{parent}' 2>/dev/null &")
