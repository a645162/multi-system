"""
GUI模块
提供PySide6图形界面功能
"""

import sys

from PySide6.QtWidgets import QApplication


def _get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def launch_main_gui():
    """启动主GUI窗口（功能选择器）"""
    from multi_system.gui.main_window import MainWindow

    app = _get_app()
    window = MainWindow()
    window.show()
    return app.exec()


def launch_port_forward_gui():
    """启动端口转发GUI"""
    from multi_system.gui.port_forward_window import PortForwardWindow

    app = _get_app()
    window = PortForwardWindow()
    window.show()
    return app.exec()
