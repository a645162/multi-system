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


def launch_feature_gui(feature_id: str):
    """根据 feature_id 启动指定功能的GUI"""
    from multi_system.gui.registry import get_by_id

    feat = get_by_id(feature_id)
    if feat is None:
        print(f"未知功能: {feature_id}")
        sys.exit(1)
    if feat.window_factory is None:
        print(f"功能 {feat.name} 不支持 GUI 启动")
        sys.exit(1)

    app = _get_app()
    win = feat.window_factory()
    win.show()
    return app.exec()


# 保持向后兼容
def launch_port_forward_gui():
    return launch_feature_gui("port-forward")


def launch_shell_toolbox_gui():
    return launch_feature_gui("shell-toolbox")
