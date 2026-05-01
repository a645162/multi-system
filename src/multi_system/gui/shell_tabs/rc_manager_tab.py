"""
Tab: RC 配置管理
"""

import subprocess
import sys
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.system.shells.rc_manager import RCManager


class _DiffDialog(QDialog):
    def __init__(self, current: str, backup: str, backup_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"对比: 当前 vs {backup_name}")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)
        splitter = QSplitter()

        left = QPlainTextEdit()
        left.setReadOnly(True)
        left.setPlainText(current)
        splitter.addWidget(left)

        right = QPlainTextEdit()
        right.setReadOnly(True)
        right.setPlainText(backup)
        splitter.addWidget(right)

        layout.addWidget(splitter)
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)


class RCManagerTab(QWidget):
    def __init__(self):
        super().__init__()
        self._manager: RCManager | None = None
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Shell:"))
        self._shell_combo = QComboBox()
        self._shell_combo.addItems(["bash", "zsh"])
        self._shell_combo.currentTextChanged.connect(self._on_shell_changed)
        top.addWidget(self._shell_combo)
        top.addStretch()
        layout.addLayout(top)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addSeparator()
        toolbar.addAction("备份当前RC", self._backup)
        toolbar.addAction("恢复选中备份", self._restore)
        toolbar.addAction("对比", self._diff)
        layout.addWidget(toolbar)

        self._preview = QPlainTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setMaximumHeight(150)
        layout.addWidget(QLabel("当前 RC 内容预览:"))
        layout.addWidget(self._preview)

        layout.addWidget(QLabel("备份列表:"))
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["备份名", "大小", "修改时间"])
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
            self._on_shell_changed(self._shell_combo.currentText())

    def _on_shell_changed(self, shell: str):
        self._manager = RCManager(shell)
        self._refresh()

    def _force_refresh(self):
        self._on_shell_changed(self._shell_combo.currentText())

    def _refresh(self):
        if not self._manager:
            return
        self._preview.setPlainText(self._manager.read_current())
        backups = self._manager.list_backups()
        self._table.setRowCount(0)
        for b in backups:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(b["name"]))
            self._table.setItem(row, 1, QTableWidgetItem(f"{b['size']} B"))
            ts = datetime.fromtimestamp(b["modified"]).strftime("%Y-%m-%d %H:%M:%S")
            self._table.setItem(row, 2, QTableWidgetItem(ts))
            self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(b["path"]))

    def _backup(self):
        if not self._manager:
            return
        path = self._manager.backup()
        QMessageBox.information(self, "备份成功", f"已备份到 {path}")
        self._refresh()

    def _restore(self):
        if not self._manager:
            return
        path = self._selected_backup_path()
        if not path:
            return
        reply = QMessageBox.warning(
            self, "确认恢复",
            f"将用 {path.name} 覆盖当前 RC 文件，是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._manager.backup("pre-restore")
            self._manager.restore(path)
            QMessageBox.information(self, "恢复成功", "RC 文件已恢复")
            self._refresh()

    def _diff(self):
        if not self._manager:
            return
        path = self._selected_backup_path()
        if not path:
            return
        current = self._manager.read_current()
        backup = self._manager.read_backup(path)
        dlg = _DiffDialog(current, backup, path.name, self)
        dlg.exec()

    def _selected_backup_path(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self._table.item(rows[0].row(), 0)
        from pathlib import Path
        return Path(item.data(Qt.ItemDataRole.UserRole)) if item else None

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)
        menu = QMenu(self)
        menu.addAction("还原备份", self._restore)
        menu.addAction("删除备份", self._delete_backup)
        menu.addSeparator()
        menu.addAction("在编辑器中打开", self._open_in_editor)
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _delete_backup(self):
        path = self._selected_backup_path()
        if not path:
            return
        reply = QMessageBox.warning(
            self, "确认删除",
            f"确定要删除备份 {path.name} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            import os
            os.remove(path)
            self._refresh()

    def _open_in_editor(self):
        path = self._selected_backup_path()
        if not path:
            return
        backup_path = str(path)
        if sys.platform == "linux":
            subprocess.Popen(["xdg-open", backup_path])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", backup_path])
        elif sys.platform == "win32":
            subprocess.Popen(["explorer", backup_path])
