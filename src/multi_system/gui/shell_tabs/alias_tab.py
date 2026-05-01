"""
Tab: Alias 管理
"""


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
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

from multi_system.system.shells.aliases import AliasEntry, AliasManager


class _AliasEditDialog(QDialog):
    def __init__(self, parent=None, entry: AliasEntry | None = None):
        super().__init__(parent)
        self.setWindowTitle("编辑 Alias" if entry else "添加 Alias")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)
        self.name_edit = QLineEdit(entry.name if entry else "")
        self.name_edit.setReadOnly(entry is not None)
        self.cmd_edit = QLineEdit(entry.command if entry else "")

        layout.addRow("Alias 名称:", self.name_edit)
        layout.addRow("命令:", self.cmd_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self) -> tuple[str, str]:
        return self.name_edit.text().strip(), self.cmd_edit.text().strip()


class AliasTab(QWidget):
    def __init__(self):
        super().__init__()
        self._manager: AliasManager | None = None
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
        toolbar.addAction("添加", self._add_alias)
        toolbar.addAction("编辑", self._edit_alias)
        toolbar.addAction("删除", self._delete_alias)
        toolbar.addSeparator()
        toolbar.addAction("同步到其他Shell", self._sync_aliases)
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Alias", "命令", "行号"])
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
        self._manager = AliasManager(shell)
        self._refresh()

    def _force_refresh(self):
        if self._manager:
            self._manager = AliasManager(self._shell_combo.currentText())
        else:
            self._on_shell_changed(self._shell_combo.currentText())
        self._refresh()

    def _refresh(self):
        if not self._manager:
            return
        self._table.setRowCount(0)
        for entry in self._manager.list_aliases():
            row = self._table.rowCount()
            self._table.insertRow(row)
            items = [
                QTableWidgetItem(entry.name),
                QTableWidgetItem(entry.command),
                QTableWidgetItem(str(entry.line_number)),
            ]
            for col, item in enumerate(items):
                item.setData(Qt.ItemDataRole.UserRole, entry.name)
                self._table.setItem(row, col, item)

    def _add_alias(self):
        if not self._manager:
            return
        dlg = _AliasEditDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, cmd = dlg.get_data()
            if name and cmd:
                self._manager.add_alias(name, cmd)
                self._refresh()

    def _edit_alias(self):
        if not self._manager:
            return
        name = self._selected_name()
        if not name:
            return
        entries = self._manager.list_aliases()
        entry = next((e for e in entries if e.name == name), None)
        if not entry:
            return
        dlg = _AliasEditDialog(self, entry=entry)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            _, cmd = dlg.get_data()
            self._manager.update_alias(name, cmd)
            self._refresh()

    def _delete_alias(self):
        if not self._manager:
            return
        name = self._selected_name()
        if name and self._manager.remove_alias(name):
            self._refresh()

    def _sync_aliases(self):
        if not self._manager:
            return
        current = self._shell_combo.currentText()
        target = "zsh" if current == "bash" else "bash"
        aliases = self._manager.list_aliases()
        if not aliases:
            return
        target_mgr = AliasManager(target)
        for a in aliases:
            target_mgr.add_alias(a.name, a.command)
        QMessageBox.information(self, "同步完成", f"已将 {len(aliases)} 个 alias 同步到 {target}")

    def _show_context_menu(self, pos):
        name = self._selected_name()
        if not name:
            return
        menu = QMenu(self)
        menu.addAction("编辑", self._edit_alias)
        menu.addAction("删除", self._delete_alias)
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _selected_name(self) -> str | None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self._table.item(rows[0].row(), 0)
        return item.text() if item else None
