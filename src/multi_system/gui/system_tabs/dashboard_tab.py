"""
Tab: 系统仪表盘
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.system.monitor.dashboard import SystemDashboard


def _fmt_bytes(b: int | float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # System info
        self._info_label = QLabel("加载中...")
        layout.addWidget(self._info_label)

        # CPU
        layout.addWidget(QLabel("<b>CPU</b>"))
        self._cpu_bar = QProgressBar()
        self._cpu_bar.setRange(0, 100)
        layout.addWidget(self._cpu_bar)
        self._cpu_label = QLabel()

        # Memory
        layout.addWidget(QLabel("<b>内存</b>"))
        self._mem_bar = QProgressBar()
        self._mem_bar.setRange(0, 100)
        layout.addWidget(self._mem_bar)
        self._mem_label = QLabel()

        # Disks
        self._disk_layout = QVBoxLayout()
        layout.addLayout(self._disk_layout)

        # Network
        self._net_label = QLabel()
        layout.addWidget(self._net_label)

        layout.addStretch()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(3000)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._refresh()

    def _refresh(self):
        info = SystemDashboard.get_system_info()
        self._info_label.setText(
            f"<b>{info.hostname}</b> | {info.os_name} {info.arch} | "
            f"CPU: {info.cpu_count_physical}核{info.cpu_count_logical}线程 | "
            f"启动: {info.boot_time.strftime('%m-%d %H:%M')}"
        )

        cpu = SystemDashboard.get_cpu_stats()
        self._cpu_bar.setValue(int(cpu.percent))
        self._cpu_label.setText(f"CPU: {cpu.percent:.1f}% | 频率: {cpu.freq_current:.0f}MHz")

        mem = SystemDashboard.get_memory_stats()
        self._mem_bar.setValue(int(mem.percent))
        self._mem_label.setText(
            f"内存: {_fmt_bytes(mem.used)} / {_fmt_bytes(mem.total)} ({mem.percent:.1f}%) | "
            f"Swap: {_fmt_bytes(mem.swap_used)} / {_fmt_bytes(mem.swap_total)} ({mem.swap_percent:.1f}%)"
        )

        # Disks — rebuild
        while self._disk_layout.count():
            item = self._disk_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for d in SystemDashboard.get_disk_stats():
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(d.percent))
            self._disk_layout.addWidget(QLabel(
                f"{d.device} → {d.mountpoint} ({d.fstype})"
            ))
            self._disk_layout.addWidget(bar)

        net = SystemDashboard.get_network_stats()
        self._net_label.setText(
            f"网络: ↑{_fmt_bytes(net.bytes_sent)} ↓{_fmt_bytes(net.bytes_recv)}"
        )
