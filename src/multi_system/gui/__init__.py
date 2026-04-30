"""
GUI模块
提供PySide6图形界面功能
"""


def launch_port_forward_gui():
    """启动端口转发GUI"""
    from PySide6.QtWidgets import QApplication
    from multi_system.gui.port_forward_window import PortForwardWindow

    import sys

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = PortForwardWindow()
    window.show()

    return app.exec()
