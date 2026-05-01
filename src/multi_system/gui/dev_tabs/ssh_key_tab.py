"""
Tab: SSH 密钥管理
"""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.program.ssh_keys import SSHKeyManager


class _GenerateKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("生成 SSH 密钥")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)
        self.name_edit = QLineEdit("id_ed25519")
        self.type_combo = QLineEdit("ed25519")
        self.type_combo.setPlaceholderText("ed25519 / rsa / ecdsa ...")
        self.passphrase_edit = QLineEdit()
        self.passphrase_edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("密钥文件名:", self.name_edit)
        layout.addRow("密钥类型:", self.type_combo)
        layout.addRow("密码短语:", self.passphrase_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "验证失败", "密钥文件名不能为空")
            return
        self.accept()

    def get_data(self) -> tuple[str, str, str]:
        return (
            self.name_edit.text().strip(),
            self.type_combo.text().strip() or "ed25519",
            self.passphrase_edit.text(),
        )


class SSHKeyTab(QWidget):
    def __init__(self):
        super().__init__()
        self._manager = SSHKeyManager()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addSeparator()
        toolbar.addAction("生成密钥", self._generate_key)
        toolbar.addAction("查看公钥", self._show_public_key)
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["文件名", "类型", "公钥", "大小"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

        layout.addWidget(QLabel("公钥内容:"))
        self._pub_view = QPlainTextEdit()
        self._pub_view.setReadOnly(True)
        self._pub_view.setMaximumHeight(100)
        layout.addWidget(self._pub_view)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._refresh()

    def _force_refresh(self):
        self._manager = SSHKeyManager()
        self._refresh()

    def _refresh(self):
        keys = self._manager.list_keys()
        self._table.setRowCount(0)
        for k in keys:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(k.name))
            self._table.setItem(row, 1, QTableWidgetItem(k.key_type))
            self._table.setItem(row, 2, QTableWidgetItem("是" if k.is_public else "否"))
            self._table.setItem(row, 3, QTableWidgetItem(self._fmt_size(k.size_bytes)))
        self._pub_view.clear()

    @staticmethod
    def _fmt_size(b: int | float) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"

    def _generate_key(self):
        dlg = _GenerateKeyDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, key_type, passphrase = dlg.get_data()
            if self._manager.generate_key(name, key_type, passphrase):
                QMessageBox.information(self, "成功", f"密钥 {name} 已生成")
                self._force_refresh()
            else:
                QMessageBox.warning(self, "失败", "密钥生成失败，请确认 ssh-keygen 可用")

    def _show_public_key(self):
        name = self._selected_key_name()
        if not name:
            return
        # If user selected a .pub file, strip the suffix
        base_name = name.removesuffix(".pub")
        pub_key = self._manager.get_public_key(base_name)
        if pub_key:
            self._pub_view.setPlainText(pub_key)
        else:
            self._pub_view.setPlainText(f"未找到 {base_name}.pub")
            QMessageBox.information(self, "提示", f"未找到 {base_name} 的公钥文件")

    def _selected_key_name(self) -> str | None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self._table.item(rows[0].row(), 0)
        return item.text() if item else None
