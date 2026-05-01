"""
Tab: 定时任务管理
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMenu,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.program.cron_manager import CronManager


class _AddCronDialog(QDialog):
    def __init__(self, parent=None, schedule: str = "", command: str = ""):
        super().__init__(parent)
        self.setWindowTitle("编辑定时任务" if schedule else "添加定时任务")
        self.setMinimumWidth(450)

        layout = QFormLayout(self)
        self.schedule_edit = QLineEdit(schedule)
        self.schedule_edit.setPlaceholderText("例: */5 * * * *")
        self.command_edit = QLineEdit(command)
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

        edit_action = menu.addAction("编辑")
        edit_action.triggered.connect(self._edit_job)

        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(self._delete_job)

        menu.addSeparator()

        cmd_item = self._table.item(row, 1)
        cmd_text = cmd_item.text() if cmd_item else ""

        copy_cmd_action = menu.addAction("复制命令")
        copy_cmd_action.triggered.connect(lambda: self._copy_to_clipboard(cmd_text))

        run_action = menu.addAction("立即执行")
        run_action.triggered.connect(lambda: self._run_job_now(cmd_text))

        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)

    def _run_job_now(self, command: str):
        if not command:
            return
        reply = QMessageBox.warning(
            self,
            "确认执行",
            f"确定要立即执行以下命令吗？\n\n{command}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        import subprocess
        try:
            subprocess.Popen(command, shell=True)
            QMessageBox.information(self, "已启动", "命令已在后台执行")
        except (FileNotFoundError, OSError) as e:
            QMessageBox.warning(self, "执行失败", f"无法执行命令: {e}")

    # --- Existing methods ---

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

    def _edit_job(self):
        line_number = self._selected_line_number()
        if line_number is None:
            return
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        schedule = self._table.item(row, 0).text() if self._table.item(row, 0) else ""
        command = self._table.item(row, 1).text() if self._table.item(row, 1) else ""

        dlg = _AddCronDialog(self, schedule=schedule, command=command)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_schedule, new_command = dlg.get_data()
            # Remove old job and add new one
            if CronManager.remove_job(line_number):
                if CronManager.add_job(new_schedule, new_command):
                    QMessageBox.information(self, "成功", "定时任务已更新")
                    self._refresh()
                else:
                    QMessageBox.warning(self, "失败", "更新定时任务失败")
            else:
                QMessageBox.warning(self, "失败", "删除旧任务失败")

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
