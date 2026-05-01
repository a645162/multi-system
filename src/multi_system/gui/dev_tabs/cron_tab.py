"""
Tab: 定时任务管理
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.program.cron_manager import CronManager


class _AddCronDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加定时任务")
        self.setMinimumWidth(450)

        layout = QFormLayout(self)
        self.schedule_edit = QLineEdit()
        self.schedule_edit.setPlaceholderText("例: */5 * * * *")
        self.command_edit = QLineEdit()
        self.command_edit.setPlaceholderText("例: /usr/bin/backup.sh")

        layout.addRow("调度表达式:", self.schedule_edit)
        layout.addRow("命令:", self.command_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _validate_and_accept(self):
        if not self.schedule_edit.text().strip() or not self.command_edit.text().strip():
            QMessageBox.warning(self, "验证失败", "调度表达式和命令不能为空")
            return
        self.accept()

    def get_data(self) -> tuple[str, str]:
        return self.schedule_edit.text().strip(), self.command_edit.text().strip()


class CronTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addSeparator()
        toolbar.addAction("添加", self._add_job)
        toolbar.addAction("删除", self._delete_job)
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["调度", "命令", "行号"])
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
        jobs = CronManager.list_jobs()
        self._table.setRowCount(0)
        for j in jobs:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(j.schedule))
            self._table.setItem(row, 1, QTableWidgetItem(j.command))
            line_item = QTableWidgetItem(str(j.line_number))
            line_item.setData(Qt.ItemDataRole.UserRole, j.line_number)
            self._table.setItem(row, 2, line_item)

    def _add_job(self):
        dlg = _AddCronDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            schedule, command = dlg.get_data()
            if CronManager.add_job(schedule, command):
                QMessageBox.information(self, "成功", "定时任务已添加")
                self._refresh()
            else:
                QMessageBox.warning(self, "失败", "添加定时任务失败，请确认 crontab 可用")

    def _delete_job(self):
        line_number = self._selected_line_number()
        if line_number is None:
            return
        reply = QMessageBox.warning(
            self,
            "确认删除",
            f"确定要删除第 {line_number} 行的定时任务吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if CronManager.remove_job(line_number):
                self._refresh()
            else:
                QMessageBox.warning(self, "失败", "删除定时任务失败")

    def _selected_line_number(self) -> int | None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self._table.item(rows[0].row(), 2)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None
