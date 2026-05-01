"""
系统仪表盘 — psutil 封装
"""

import platform
from dataclasses import dataclass
from datetime import datetime

import psutil


@dataclass
class SystemInfo:
    hostname: str
    os_name: str
    os_version: str
    arch: str
    boot_time: datetime
    cpu_count_logical: int
    cpu_count_physical: int


@dataclass
class CpuStats:
    percent: float
    per_cpu: list[float]
    freq_current: float
    freq_max: float


@dataclass
class MemoryStats:
    total: int
    used: int
    available: int
    percent: float
    swap_total: int
    swap_used: int
    swap_percent: float


@dataclass
class DiskStats:
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float


@dataclass
class NetworkStats:
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int


class SystemDashboard:
    @staticmethod
    def get_system_info() -> SystemInfo:
        return SystemInfo(
            hostname=platform.node(),
            os_name=platform.system(),
            os_version=platform.version(),
            arch=platform.machine(),
            boot_time=datetime.fromtimestamp(psutil.boot_time()),
            cpu_count_logical=psutil.cpu_count(logical=True),
            cpu_count_physical=psutil.cpu_count(logical=False),
        )

    @staticmethod
    def get_cpu_stats() -> CpuStats:
        freq = psutil.cpu_freq()
        return CpuStats(
            percent=psutil.cpu_percent(interval=0.5),
            per_cpu=psutil.cpu_percent(interval=0.5, percpu=True),
            freq_current=freq.current if freq else 0.0,
            freq_max=freq.max if freq else 0.0,
        )

    @staticmethod
    def get_memory_stats() -> MemoryStats:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return MemoryStats(
            total=mem.total, used=mem.used, available=mem.available, percent=mem.percent,
            swap_total=swap.total, swap_used=swap.used, swap_percent=swap.percent,
        )

    @staticmethod
    def get_disk_stats() -> list[DiskStats]:
        disks = []
        for p in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(p.mountpoint)
                disks.append(DiskStats(
                    device=p.device, mountpoint=p.mountpoint, fstype=p.fstype,
                    total=usage.total, used=usage.used, free=usage.free, percent=usage.percent,
                ))
            except PermissionError:
                continue
        return disks

    @staticmethod
    def get_network_stats() -> NetworkStats:
        net = psutil.net_io_counters()
        return NetworkStats(
            bytes_sent=net.bytes_sent, bytes_recv=net.bytes_recv,
            packets_sent=net.packets_sent, packets_recv=net.packets_recv,
        )
