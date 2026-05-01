"""
Tab: RC 配置管理
"""

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
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
        left.setWindowTitle("当前")
        splitter.addWidget(left)

        right = QPlainTextEdit()
        right.setReadOnly(True)
        right.setPlainText(backup)
        right.setWindowTitle("备份")
        splitter.addWidget(right)

        layout.addWidget(splitter)
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)


class RCManagerTab(QWidget):
    def __init__(self):
        super().__init__()
        self._manager: RCManager | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Shell selector
        top = QHBoxLayout()
        top.addWidget(QLabel("Shell:"))
        self._shell_combo = QComboBox()
        self._shell_combo.addItems(["bash", "zsh"])
        self._shell_combo.currentTextChanged.connect(self._on_shell_changed)
        top.addWidget(self._shell_combo)
        top.addStretch()
        layout.addLayout(top)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("备份当前RC", self._backup)
        self._restore_action = toolbar.addAction("恢复选中备份", self._restore)
        self._diff_action = toolbar.addAction("对比", self._diff)
        toolbar.addAction("刷新", self._refresh)
        layout.addWidget(toolbar)

        # RC content preview
        self._preview = QPlainTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setMaximumHeight(150)
        layout.addWidget(QLabel("当前 RC 内容预览:"))
        layout.addWidget(self._preview)

        # Backup list
        layout.addWidget(QLabel("备份列表:"))
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["备份名", "大小", "修改时间"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

    def _on_shell_changed(self, shell: str):
        self._manager = RCManager(shell)
        self._refresh()

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
