"""
网络工具箱
"""

from multi_system.gui.base_toolbox import BaseToolboxWindow
from multi_system.gui.network_tabs.dns_tab import DNSTab
from multi_system.gui.network_tabs.port_scan_tab import PortScanTab
from multi_system.gui.network_tabs.proxy_tab import ProxyTab
from multi_system.gui.network_tabs.speed_tab import SpeedTab


class NetworkToolboxWindow(BaseToolboxWindow):
    TABS = [
        (DNSTab, "DNS 切换"),
        (ProxyTab, "代理管理"),
        (SpeedTab, "网速测试"),
        (PortScanTab, "端口扫描"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("网络工具箱")
