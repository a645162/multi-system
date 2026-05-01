"""
Tab: 代理管理
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.network.proxy_manager import ProxyConfig, ProxyManager


class ProxyTab(QWidget):
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

        # --- HTTP Proxy ---
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("HTTP 代理:"))
        self._http_edit = QLineEdit()
        self._http_edit.setPlaceholderText("http://127.0.0.1:7890")
        h1.addWidget(self._http_edit)
        layout.addLayout(h1)

        # --- HTTPS Proxy ---
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("HTTPS 代理:"))
        self._https_edit = QLineEdit()
        self._https_edit.setPlaceholderText("http://127.0.0.1:7890")
        h2.addWidget(self._https_edit)
        layout.addLayout(h2)

        # --- No Proxy ---
        h3 = QHBoxLayout()
        h3.addWidget(QLabel("No Proxy:"))
        self._no_proxy_edit = QLineEdit()
        self._no_proxy_edit.setPlaceholderText("localhost,127.0.0.1")
        self._no_proxy_edit.setText("localhost,127.0.0.1")
        h3.addWidget(self._no_proxy_edit)
        layout.addLayout(h3)

        # --- Current proxy display ---
        layout.addWidget(QLabel("<b>当前代理状态</b>"))
        self._current_label = QLabel("未检测")
        self._current_label.setWordWrap(True)
        self._current_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._current_label)

        # --- Action buttons ---
        btn_row = QHBoxLayout()
        self._apply_btn = QPushButton("应用")
        self._apply_btn.clicked.connect(self._on_apply)
        btn_row.addWidget(self._apply_btn)

        self._clear_btn = QPushButton("清除代理")
        self._clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(self._clear_btn)
        layout.addLayout(btn_row)

        layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._refresh()

    def _refresh(self):
        config = ProxyManager.get_proxy()
        self._http_edit.setText(config.http)
        self._https_edit.setText(config.https)
        self._no_proxy_edit.setText(config.no_proxy)

        parts = []
        if config.http:
            parts.append(f"http_proxy = {config.http}")
        if config.https:
            parts.append(f"https_proxy = {config.https}")
        if config.no_proxy:
            parts.append(f"no_proxy = {config.no_proxy}")
        self._current_label.setText("\n".join(parts) if parts else "未设置代理")

    def _on_apply(self):
        config = ProxyConfig(
            http=self._http_edit.text().strip(),
            https=self._https_edit.text().strip(),
            no_proxy=self._no_proxy_edit.text().strip() or "localhost,127.0.0.1",
        )
        ProxyManager.set_proxy(config)
        QMessageBox.information(self, "成功", "代理已应用（当前进程环境变量已更新）")
        self._refresh()

    def _on_clear(self):
        ProxyManager.clear_proxy()
        QMessageBox.information(self, "成功", "代理已清除")
        self._refresh()
