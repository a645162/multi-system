"""
Tab: DNS 切换
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.network.dns_switcher import PRESET_DNS, DNSSwitcher


class DNSTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._refresh)
        layout.addWidget(toolbar)

        # --- Preset selector ---
        row = QHBoxLayout()
        row.addWidget(QLabel("预设 DNS:"))
        self._preset_combo = QComboBox()
        self._preset_combo.addItems(list(PRESET_DNS.keys()) + ["自定义"])
        self._preset_combo.currentTextChanged.connect(self._on_preset_changed)
        row.addWidget(self._preset_combo)
        layout.addLayout(row)

        # --- Custom DNS inputs ---
        self._custom_widget = QWidget()
        custom_layout = QVBoxLayout(self._custom_widget)
        custom_layout.setContentsMargins(0, 0, 0, 0)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("主 DNS:"))
        self._dns1_edit = QLineEdit()
        self._dns1_edit.setPlaceholderText("例如 8.8.8.8")
        h1.addWidget(self._dns1_edit)
        custom_layout.addLayout(h1)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("备 DNS:"))
        self._dns2_edit = QLineEdit()
        self._dns2_edit.setPlaceholderText("例如 8.8.4.4")
        h2.addWidget(self._dns2_edit)
        custom_layout.addLayout(h2)

        self._custom_widget.setVisible(False)
        layout.addWidget(self._custom_widget)

        # --- Current DNS display ---
        layout.addWidget(QLabel("<b>当前 DNS</b>"))
        self._current_label = QLabel("未检测")
        self._current_label.setWordWrap(True)
        self._current_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._current_label)

        # --- Action buttons ---
        btn_row = QHBoxLayout()
        self._apply_btn = QPushButton("应用")
        self._apply_btn.clicked.connect(self._on_apply)
        btn_row.addWidget(self._apply_btn)

        self._reset_btn = QPushButton("恢复 DHCP")
        self._reset_btn.clicked.connect(self._on_reset)
        btn_row.addWidget(self._reset_btn)
        layout.addLayout(btn_row)

        layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._refresh()

    def _on_preset_changed(self, text: str):
        self._custom_widget.setVisible(text == "自定义")

    def _refresh(self):
        servers = DNSSwitcher.get_current()
        if servers:
            self._current_label.setText("\n".join(servers))
        else:
            self._current_label.setText("无法获取当前 DNS（可能需要管理员权限）")

    def _on_apply(self):
        preset = self._preset_combo.currentText()
        if preset == "自定义":
            dns_list = [self._dns1_edit.text().strip()]
            dns2 = self._dns2_edit.text().strip()
            if dns2:
                dns_list.append(dns2)
            if not dns_list[0]:
                QMessageBox.warning(self, "输入错误", "请填写主 DNS 地址")
                return
        else:
            dns_list = [s.ip for s in PRESET_DNS[preset]]

        ok = DNSSwitcher.set_dns(dns_list)
        if ok:
            QMessageBox.information(self, "成功", f"DNS 已设置为: {', '.join(dns_list)}")
            self._refresh()
        else:
            QMessageBox.warning(self, "失败", "设置 DNS 失败，可能需要管理员/root 权限")

    def _on_reset(self):
        ok = DNSSwitcher.reset_dns()
        if ok:
            QMessageBox.information(self, "成功", "DNS 已恢复为 DHCP 自动获取")
            self._refresh()
        else:
            QMessageBox.warning(self, "失败", "恢复 DHCP DNS 失败，可能需要管理员/root 权限")
