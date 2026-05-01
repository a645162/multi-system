"""
Tab: SSH 密钥管理
"""

import os
import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMenu,
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
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
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

    # --- Context menu ---

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)

        menu = QMenu(self)

        copy_pub_action = menu.addAction("复制公钥")
        copy_pub_action.triggered.connect(self._copy_public_key)

        delete_action = menu.addAction("删除密钥")
        delete_action.triggered.connect(self._delete_key)

        menu.addSeparator()

        open_dir_action = menu.addAction("在文件管理器中显示")
        open_dir_action.triggered.connect(self._open_ssh_dir)

        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_public_key(self):
        name = self._selected_key_name()
        if not name:
            return
        base_name = name.removesuffix(".pub")
        pub_key = self._manager.get_public_key(base_name)
        if pub_key:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(pub_key)
            self._pub_view.setPlainText(pub_key)
        else:
            QMessageBox.information(self, "提示", f"未找到 {base_name} 的公钥文件")

    def _delete_key(self):
        name = self._selected_key_name()
        if not name:
            return
        base_name = name.removesuffix(".pub")
        ssh_dir = os.path.expanduser("~/.ssh")
        key_path = os.path.join(ssh_dir, base_name)
        pub_path = key_path + ".pub"

        reply = QMessageBox.warning(
            self,
            "确认删除",
            f"确定要删除密钥 {base_name} 吗？\n\n将删除:\n{key_path}\n{pub_path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            if os.path.exists(key_path):
                os.remove(key_path)
            if os.path.exists(pub_path):
                os.remove(pub_path)
            QMessageBox.information(self, "成功", f"密钥 {base_name} 已删除")
            self._force_refresh()
        except OSError as e:
            QMessageBox.warning(self, "失败", f"删除密钥失败: {e}")

    def _open_ssh_dir(self):
        ssh_dir = os.path.expanduser("~/.ssh")
        if not os.path.isdir(ssh_dir):
            QMessageBox.information(self, "提示", "~/.ssh 目录不存在")
            return
        try:
            if sys.platform == "linux":
                subprocess.Popen(["xdg-open", ssh_dir])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", ssh_dir])
            elif sys.platform == "win32":
                subprocess.Popen(["explorer", ssh_dir])
        except (FileNotFoundError, OSError):
            QMessageBox.warning(self, "失败", "无法打开文件管理器")

    # --- Existing methods ---

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
