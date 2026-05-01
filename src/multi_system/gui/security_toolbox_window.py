from multi_system.gui.base_toolbox import BaseToolboxWindow
from multi_system.gui.security_tabs.file_audit_tab import FileAuditTab
from multi_system.gui.security_tabs.firewall_tab import FirewallTab
from multi_system.gui.security_tabs.port_scan_tab import SecurityPortScanTab


class SecurityToolboxWindow(BaseToolboxWindow):
    TABS = [
        (FirewallTab, "防火墙"),
        (SecurityPortScanTab, "端口扫描"),
        (FileAuditTab, "权限审计"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("安全工具箱")
