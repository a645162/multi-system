"""
Tab: 网速测试
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.network.speed_test import SpeedResult, SpeedTester


class SpeedTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._testing = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._refresh)
        layout.addWidget(toolbar)

        # --- Test button ---
        btn_row = QHBoxLayout()
        self._test_btn = QPushButton("测速")
        self._test_btn.setFixedHeight(40)
        self._test_btn.clicked.connect(self._on_test)
        btn_row.addWidget(self._test_btn)
        layout.addLayout(btn_row)

        # --- Progress ---
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # indeterminate
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # --- Results ---
        self._result_label = QLabel("点击「测速」开始")
        self._result_label.setWordWrap(True)
        self._result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._result_label)

        layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._refresh()

    def _refresh(self):
        if not self._testing:
            self._result_label.setText("点击「测速」开始")

    def _on_test(self):
        if self._testing:
            return
        self._testing = True
        self._test_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._result_label.setText("正在 Ping ...")

        # Run ping first, then download
        QTimer.singleShot(0, self._run_ping)

    def _run_ping(self):
        try:
            ping_ms = SpeedTester.ping()
        except Exception:
            ping_ms = -1.0

        if ping_ms < 0:
            self._show_result(SpeedResult(ping_ms=-1.0, error="Ping 失败，网络可能不可用"))
            return

        self._result_label.setText(f"Ping: {ping_ms:.1f} ms\n正在下载测试 ...")
        QTimer.singleShot(0, lambda: self._run_download(ping_ms))

    def _run_download(self, ping_ms: float):
        try:
            result = SpeedTester.download_test()
            result.ping_ms = ping_ms
        except Exception as e:
            result = SpeedResult(ping_ms=ping_ms, error=str(e))
        self._show_result(result)

    def _show_result(self, result: SpeedResult):
        self._testing = False
        self._test_btn.setEnabled(True)
        self._progress.setVisible(False)

        if result.error:
            self._result_label.setText(
                f"Ping: {result.ping_ms:.1f} ms\n下载测试失败: {result.error}"
            )
        else:
            self._result_label.setText(
                f"Ping: {result.ping_ms:.1f} ms\n"
                f"下载速度: {result.download_mbps:.2f} Mbps"
            )
