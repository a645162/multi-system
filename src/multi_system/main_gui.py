import sys

_GUI_COMMANDS = {
    "port-forward": ("端口转发工具", "launch_port_forward_gui"),
    "shell-toolbox": ("Shell工具箱", "launch_shell_toolbox_gui"),
}


def main():
    args = sys.argv[1:]

    if not args:
        _launch_main()
        return

    if args[0] in ("--help", "-h"):
        _print_help()
        return

    cmd = args[0]
    if cmd not in _GUI_COMMANDS:
        print(f"未知命令: {cmd}")
        print("使用 --help 查看可用命令")
        sys.exit(1)

    _dispatch(cmd)


def _print_help():
    print("Usage: multi-system-gui [command]")
    print()
    print("不带参数启动主窗口，可选择功能")
    print()
    print("Commands:")
    for cmd, (desc, *_) in _GUI_COMMANDS.items():
        print(f"  {cmd:<16} {desc}")


def _launch_main():
    try:
        from multi_system.gui import launch_main_gui
        launch_main_gui()
    except ImportError as e:
        print(f"错误: {e}")
        print("请运行: pip install multi-system[gui]")
        sys.exit(1)


def _dispatch(cmd: str):
    _, func_name = _GUI_COMMANDS[cmd]
    try:
        from multi_system.gui import __dict__ as gui_module
        func = gui_module[func_name]
        func()
    except (ImportError, KeyError) as e:
        print(f"错误: {e}")
        print("请运行: pip install multi-system[gui]")
        sys.exit(1)


if __name__ == "__main__":
    main()
