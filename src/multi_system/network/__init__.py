"""
网络相关工具模块
"""

from .dns_switcher import PRESET_DNS, DNSServer, DNSSwitcher
from .ntp_servers import NTPManager, NTPServer
from .port_forward import PortForwardEngine, PortForwardRule, RuleStatus
from .port_scanner import COMMON_PORTS, PortResult, PortScanner
from .proxy_manager import ProxyConfig, ProxyManager
from .speed_test import SpeedResult, SpeedTester

__all__ = [
    "NTPServer",
    "NTPManager",
    "PortForwardRule",
    "PortForwardEngine",
    "RuleStatus",
    "DNSSwitcher",
    "DNSServer",
    "PRESET_DNS",
    "ProxyManager",
    "ProxyConfig",
    "SpeedTester",
    "SpeedResult",
    "PortScanner",
    "PortResult",
    "COMMON_PORTS",
]
