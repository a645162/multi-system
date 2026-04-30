"""
端口转发GUI主窗口
"""

from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QSpinBox,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.network.port_forward import PortForwardRule, RuleStatus
from multi_system.gui.port_forward_worker import PortForwardWorker

_STATUS_TEXT = {
    RuleStatus.STOPPED: "已停止",
    RuleStatus.STARTING: "启动中...",
    RuleStatus.RUNNING: "运行中",
    RuleStatus.ERROR: "错误",
}

_STATUS_COLOR = {
    RuleStatus.RUNNING: QColor(200, 255, 200),
    RuleStatus.ERROR: QColor(255, 200, 200),
    RuleStatus.STARTING: QColor(255, 255, 200),
}

COL_NAME = 0
COL_LOCAL = 1
COL_REMOTE = 2
COL_STATUS = 3
COL_CONNECTIONS = 4
COL_COUNT = 5


class AddRuleDialog(QDialog):
    def __init__(self, parent=None, rule: Optional[PortForwardRule] = None):
        super().__init__(parent)
        self.setWindowTitle("编辑规则" if rule else "添加规则")
        self.setMinimumWidth(380)

        layout = QFormLayout(self)

        self.name_edit = QLineEdit(rule.name if rule else "")
        self.local_host_edit = QLineEdit(rule.local_host if rule else "127.0.0.1")
        self.local_port_spin = QSpinBox()
        self.local_port_spin.setRange(1, 65535)
        self.local_port_spin.setValue(rule.local_port if rule else 8080)
        self.remote_host_edit = QLineEdit(rule.remote_host if rule else "")
        self.remote_port_spin = QSpinBox()
        self.remote_port_spin.setRange(1, 65535)
        self.remote_port_spin.setValue(rule.remote_port if rule else 80)

        layout.addRow("名称:", self.name_edit)
        layout.addRow("本地地址:", self.local_host_edit)
        layout.addRow("本地端口:", self.local_port_spin)
        layout.addRow("远程地址:", self.remote_host_edit)
        layout.addRow("远程端口:", self.remote_port_spin)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_rule_data(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "local_host": self.local_host_edit.text().strip(),
            "local_port": self.local_port_spin.value(),
            "remote_host": self.remote_host_edit.text().strip(),
            "remote_port": self.remote_port_spin.value(),
        }

    def _validate_and_accept(self):
        data = self.get_rule_data()
        if not data["remote_host"]:
            QMessageBox.warning(self, "验证失败", "远程地址不能为空")
            return
        import sys
        if sys.platform == "linux" and data["local_port"] < 1024:
            reply = QMessageBox.warning(
                self, "权限提醒",
                "Linux 下绑定 1024 以下端口需要 root 权限，是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return
        self.accept()


class PortForwardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("端口转发工具")
        self.setMinimumSize(QSize(750, 450))

        self._worker = PortForwardWorker(self)
        self._worker.rule_status_changed.connect(self._on_rule_status_changed)
        self._worker.rule_connection_count_changed.connect(self._on_connection_count_changed)
        self._worker.error_occurred.connect(self._on_error)

        self._init_ui()
        self._worker.start()

    def _init_ui(self):
        toolbar = QToolBar("工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self._add_action = QAction("添加规则", self)
        self._add_action.triggered.connect(self._add_rule)
        toolbar.addAction(self._add_action)

        self._delete_action = QAction("删除规则", self)
        self._delete_action.triggered.connect(self._delete_rule)
        self._delete_action.setEnabled(False)
        toolbar.addAction(self._delete_action)

        toolbar.addSeparator()

        self._start_action = QAction("启动", self)
        self._start_action.triggered.connect(self._start_rule)
        self._start_action.setEnabled(False)
        toolbar.addAction(self._start_action)

        self._stop_action = QAction("停止", self)
        self._stop_action.triggered.connect(self._stop_rule)
        self._stop_action.setEnabled(False)
        toolbar.addAction(self._stop_action)

        toolbar.addSeparator()

        self._start_all_action = QAction("全部启动", self)
        self._start_all_action.triggered.connect(self._start_all)
        toolbar.addAction(self._start_all_action)

        self._stop_all_action = QAction("全部停止", self)
        self._stop_all_action.triggered.connect(self._stop_all)
        toolbar.addAction(self._stop_all_action)

        self._table = QTableWidget(0, COL_COUNT)
        self._table.setHorizontalHeaderLabels(["名称", "本地地址", "远程地址", "状态", "连接数"])
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.selectionModel().selectionChanged.connect(self._update_action_states)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self._table)
        self.setCentralWidget(central)

        self.statusBar().showMessage("就绪")

    def closeEvent(self, event):
        self._worker.stop_all_rules()
        self._worker.stop()
        self._worker.wait(3000)
        event.accept()

    def _add_rule(self):
        dialog = AddRuleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_rule_data()
            rule = PortForwardRule(**data)
            self._worker.add_rule(rule)
            self._refresh_table()

    def _delete_rule(self):
        rule_id = self._selected_rule_id()
        if not rule_id:
            return
        rule = self._worker.get_all_rules()
        for r in rule:
            if r.id == rule_id and r.status == RuleStatus.RUNNING:
                QMessageBox.warning(self, "无法删除", "请先停止规则再删除")
                return
        if self._worker.remove_rule(rule_id):
            self._refresh_table()

    def _start_rule(self):
        rule_id = self._selected_rule_id()
        if rule_id:
            self._worker.start_rule(rule_id)

    def _stop_rule(self):
        rule_id = self._selected_rule_id()
        if rule_id:
            self._worker.stop_rule(rule_id)

    def _start_all(self):
        for rule in self._worker.get_all_rules():
            if rule.status == RuleStatus.STOPPED or rule.status == RuleStatus.ERROR:
                self._worker.start_rule(rule.id)

    def _stop_all(self):
        self._worker.stop_all_rules()

    def _on_rule_status_changed(self, rule_id: str, status: str, error: str):
        row = self._find_row(rule_id)
        if row < 0:
            self._refresh_table()
            return

        status_enum = RuleStatus(status)
        item = QTableWidgetItem(_STATUS_TEXT[status_enum])
        item.setData(Qt.ItemDataRole.UserRole, rule_id)
        color = _STATUS_COLOR.get(status_enum)
        if color:
            item.setBackground(color)
        self._table.setItem(row, COL_STATUS, item)

        if status_enum == RuleStatus.ERROR and error:
            self._table.item(row, COL_STATUS).setToolTip(error)

        self._update_action_states()
        self.statusBar().showMessage(f"规则 {rule_id[:8]}... {_STATUS_TEXT[status_enum]}")

    def _on_connection_count_changed(self, rule_id: str, count: int):
        row = self._find_row(rule_id)
        if row >= 0:
            item = QTableWidgetItem(str(count))
            item.setData(Qt.ItemDataRole.UserRole, rule_id)
            self._table.setItem(row, COL_CONNECTIONS, item)

    def _on_error(self, message: str):
        self.statusBar().showMessage(f"错误: {message}")

    def _refresh_table(self):
        self._table.setRowCount(0)
        for rule in self._worker.get_all_rules():
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._set_row_data(row, rule)
        self._update_action_states()

    def _set_row_data(self, row: int, rule: PortForwardRule):
        items = [
            QTableWidgetItem(rule.name or rule.id[:8]),
            QTableWidgetItem(f"{rule.local_host}:{rule.local_port}"),
            QTableWidgetItem(f"{rule.remote_host}:{rule.remote_port}"),
            QTableWidgetItem(_STATUS_TEXT[rule.status]),
            QTableWidgetItem(str(rule.active_connections)),
        ]
        color = _STATUS_COLOR.get(rule.status)
        for col, item in enumerate(items):
            item.setData(Qt.ItemDataRole.UserRole, rule.id)
            if color:
                item.setBackground(color)
            self._table.setItem(row, col, item)

    def _find_row(self, rule_id: str) -> int:
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == rule_id:
                return row
        return -1

    def _selected_rule_id(self) -> Optional[str]:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self._table.item(rows[0].row(), 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _update_action_states(self):
        rule_id = self._selected_rule_id()
        if not rule_id:
            self._delete_action.setEnabled(False)
            self._start_action.setEnabled(False)
            self._stop_action.setEnabled(False)
            return

        rules = self._worker.get_all_rules()
        rule = next((r for r in rules if r.id == rule_id), None)
        if rule is None:
            return

        stopped = rule.status in (RuleStatus.STOPPED, RuleStatus.ERROR)
        self._delete_action.setEnabled(stopped)
        self._start_action.setEnabled(stopped)
        self._stop_action.setEnabled(rule.status == RuleStatus.RUNNING)
