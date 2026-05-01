"""
Tab: Prompt 主题
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.system.shells.prompt_themes import PromptThemeManager


class _CustomPromptDialog(QDialog):
    def __init__(self, shell: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义 Prompt")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        key = "PS1" if shell == "bash" else "PROMPT"
        layout.addWidget(QLabel(f"输入 {key} 值:"))

        self._edit = QPlainTextEdit()
        self._edit.setPlaceholderText(r'例: \u@\h:\w\$ ')
        layout.addWidget(self._edit)

        btn = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)

    def get_value(self) -> str:
        return self._edit.toPlainText().strip()


class PromptTab(QWidget):
    def __init__(self):
        super().__init__()
        self._manager: PromptThemeManager | None = None
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
        toolbar.addAction("应用选中主题", self._apply_selected)
        toolbar.addAction("自定义 Prompt", self._apply_custom)
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["主题", "描述", "Prompt 值"])
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
        self._manager = PromptThemeManager(shell)
        self._refresh()

    def _force_refresh(self):
        self._on_shell_changed(self._shell_combo.currentText())

    def _refresh(self):
        if not self._manager:
            return
        self._table.setRowCount(0)
        for theme in self._manager.list_themes():
            row = self._table.rowCount()
            self._table.insertRow(row)
            ps1 = theme.bash_ps1 if self._manager.shell == "bash" else theme.zsh_prompt
            items = [
                QTableWidgetItem(theme.name),
                QTableWidgetItem(theme.description),
                QTableWidgetItem(ps1),
            ]
            for col, item in enumerate(items):
                item.setData(Qt.ItemDataRole.UserRole, theme.name)
                self._table.setItem(row, col, item)

    def _apply_selected(self):
        if not self._manager:
            return
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        name = self._table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        theme = self._manager.get_theme(name)
        if theme:
            self._manager.backup("pre-prompt")
            self._manager.apply_theme(theme)
            QMessageBox.information(self, "应用成功", f"已应用主题: {theme.name}\n重新打开终端即可生效")

    def _apply_custom(self):
        if not self._manager:
            return
        dlg = _CustomPromptDialog(self._manager.shell, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            value = dlg.get_value()
            if value:
                self._manager.backup("pre-prompt")
                self._manager.apply_custom(value)
                QMessageBox.information(self, "应用成功", "自定义 Prompt 已应用")

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)
        menu = QMenu(self)
        menu.addAction("应用主题", self._apply_selected)
        menu.addAction("复制 Prompt 值", self._copy_prompt_value)
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_prompt_value(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 2)
        if item:
            QApplication.clipboard().setText(item.text())
