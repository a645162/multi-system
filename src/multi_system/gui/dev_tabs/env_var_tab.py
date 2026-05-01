"""
Tab: 环境变量管理
"""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
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

from multi_system.program.env_var_manager import EnvVarManager


class _EnvVarEditDialog(QDialog):
    def __init__(self, parent=None, name: str = "", value: str = ""):
        super().__init__(parent)
        self.setWindowTitle("编辑环境变量" if name else "添加环境变量")
        self.setMinimumWidth(450)

        layout = QFormLayout(self)
        self.name_edit = QLineEdit(name)
        self.name_edit.setReadOnly(bool(name))
        self.value_edit = QLineEdit(value)

        layout.addRow("变量名:", self.name_edit)
        layout.addRow("变量值:", self.value_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "验证失败", "变量名不能为空")
            return
        self.accept()

    def get_data(self) -> tuple[str, str]:
        return self.name_edit.text().strip(), self.value_edit.text().strip()


class EnvVarTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("搜索:"))
        self._search = QLineEdit()
        self._search.setPlaceholderText("变量名或值...")
        self._search.textChanged.connect(self._on_search)
        top.addWidget(self._search)
        layout.addLayout(top)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addSeparator()
        toolbar.addAction("添加", self._add_var)
        toolbar.addAction("编辑", self._edit_var)
        toolbar.addAction("删除", self._delete_var)
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["变量名", "值", "来源"])
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
        entries = EnvVarManager.list_vars()
        self._show_entries(entries)

    def _on_search(self, keyword: str):
        if not keyword:
            self._refresh()
            return
        entries = EnvVarManager.search(keyword)
        self._show_entries(entries)

    def _show_entries(self, entries):
        self._table.setRowCount(0)
        for e in entries:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(e.name))
            self._table.setItem(row, 1, QTableWidgetItem(e.value))
            self._table.setItem(row, 2, QTableWidgetItem(e.source))

    def _add_var(self):
        dlg = _EnvVarEditDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, value = dlg.get_data()
            if name:
                EnvVarManager.set_var(name, value)
                self._refresh()

    def _edit_var(self):
        name = self._selected_name()
        if not name:
            return
        import os
        current_value = os.environ.get(name, "")
        dlg = _EnvVarEditDialog(self, name=name, value=current_value)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            _, value = dlg.get_data()
            EnvVarManager.set_var(name, value)
            self._refresh()

    def _delete_var(self):
        name = self._selected_name()
        if not name:
            return
        reply = QMessageBox.warning(
            self,
            "确认删除",
            f"确定要删除环境变量 {name} 吗？\n（仅删除当前进程环境，不影响系统/Shell配置）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            EnvVarManager.delete_var(name)
            self._refresh()

    def _selected_name(self) -> str | None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self._table.item(rows[0].row(), 0)
        return item.text() if item else None
