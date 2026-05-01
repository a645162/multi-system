from multi_system.gui.base_toolbox import BaseToolboxWindow
from multi_system.gui.dev_tabs.cron_tab import CronTab
from multi_system.gui.dev_tabs.env_var_tab import EnvVarTab
from multi_system.gui.dev_tabs.log_tab import LogTab
from multi_system.gui.dev_tabs.ssh_key_tab import SSHKeyTab


class DevToolboxWindow(BaseToolboxWindow):
    TABS = [
        (EnvVarTab, "环境变量"),
        (SSHKeyTab, "SSH 密钥"),
        (CronTab, "定时任务"),
        (LogTab, "日志查看"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("开发工具箱")
