"""
Tab: 防火墙管理
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.system.security.firewall import FirewallManager


class FirewallTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Status display ---
        status_row = QHBoxLayout()
        status_row.addWidget(QLabel("防火墙状态:"))
        self._status_label = QLabel("未知")
        self._status_label.setWordWrap(True)
        status_row.addWidget(self._status_label)
        self._enable_btn = QPushButton("启用")
        self._enable_btn.clicked.connect(lambda: self._toggle_firewall(True))
        status_row.addWidget(self._enable_btn)
        self._disable_btn = QPushButton("禁用")
        self._disable_btn.clicked.connect(lambda: self._toggle_firewall(False))
        status_row.addWidget(self._disable_btn)
        layout.addLayout(status_row)

        # --- Add rule ---
        rule_row = QHBoxLayout()
        rule_row.addWidget(QLabel("端口:"))
        self._port_spin = QSpinBox()
        self._port_spin.setRange(1, 65535)
        self._port_spin.setValue(80)
        rule_row.addWidget(self._port_spin)
        rule_row.addWidget(QLabel("动作:"))
        self._action_combo = QComboBox()
        self._action_combo.addItems(["allow", "deny"])
        rule_row.addWidget(self._action_combo)
        rule_row.addWidget(QLabel("协议:"))
        self._protocol_combo = QComboBox()
        self._protocol_combo.addItems(["tcp", "udp"])
        rule_row.addWidget(self._protocol_combo)
        self._add_rule_btn = QPushButton("添加规则")
        self._add_rule_btn.clicked.connect(self._add_rule)
        rule_row.addWidget(self._add_rule_btn)
        layout.addLayout(rule_row)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addAction("删除规则", self._delete_selected_rule)
        layout.addWidget(toolbar)

        # --- Rules table ---
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["规则", "动作", "端口", "协议", "方向"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._table)

        # --- Raw status output ---
        layout.addWidget(QLabel("原始状态输出:"))
        self._raw_output = QPlainTextEdit()
        self._raw_output.setReadOnly(True)
        self._raw_output.setMaximumHeight(120)
        layout.addWidget(self._raw_output)

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

        delete_action = menu.addAction("删除规则")
        delete_action.triggered.connect(self._delete_selected_rule)

        menu.addSeparator()

        rule_item = self._table.item(row, 0)
        rule_text = rule_item.text() if rule_item else ""

        copy_action = menu.addAction("复制规则文本")
        copy_action.triggered.connect(lambda: self._copy_to_clipboard(rule_text))

        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)

    # --- Existing methods ---

    def _force_refresh(self):
        self._refresh()

    def _refresh(self):
        status = FirewallManager.get_status()
        self._status_label.setText(status or "未知")
        self._raw_output.setPlainText(status)

        rules = FirewallManager.list_rules()
        self._table.setRowCount(0)
        for r in rules:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(r.name))
            self._table.setItem(row, 1, QTableWidgetItem(r.action))
            self._table.setItem(row, 2, QTableWidgetItem(r.port))
            self._table.setItem(row, 3, QTableWidgetItem(r.protocol))
            self._table.setItem(row, 4, QTableWidgetItem(r.direction))

    def _toggle_firewall(self, enabled: bool):
        reply = QMessageBox.warning(
            self,
            "确认",
            f"确定要{'启用' if enabled else '禁用'}防火墙吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if FirewallManager.toggle(enabled):
            QMessageBox.information(self, "成功", f"防火墙已{'启用' if enabled else '禁用'}")
            self._refresh()
        else:
            QMessageBox.warning(self, "失败", "操作失败，可能需要管理员权限")

    def _add_rule(self):
        port = self._port_spin.value()
        action = self._action_combo.currentText()
        protocol = self._protocol_combo.currentText()
        reply = QMessageBox.warning(
            self,
            "确认",
            f"确定要添加规则: {action} {port}/{protocol} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if FirewallManager.add_rule(port, action, protocol):
            QMessageBox.information(self, "成功", "规则已添加")
            self._refresh()
        else:
            QMessageBox.warning(self, "失败", "添加规则失败，可能需要管理员权限")

    # --- New actions ---

    def _delete_selected_rule(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        rule_item = self._table.item(row, 0)
        if not rule_item:
            return
        rule_name = rule_item.text()
        reply = QMessageBox.warning(
            self,
            "确认删除",
            f"确定要删除防火墙规则吗？\n\n{rule_name}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if FirewallManager.delete_rule(rule_name):
            QMessageBox.information(self, "成功", "规则已删除")
            self._refresh()
        else:
            QMessageBox.warning(self, "失败", "删除规则失败，可能需要管理员权限")
