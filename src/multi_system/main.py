import sys


def main():
    if len(sys.argv) > 1:
        subcommand = sys.argv[1]
        if subcommand == "port-forward":
            _launch_port_forward()
            return
        if subcommand in ("--help", "-h"):
            _print_help()
            return

    print("Multi-system package is working!")
    print("Usage: multi-system [port-forward]")


def _print_help():
    print("Usage: multi-system [command]")
    print()
    print("Commands:")
    print("  port-forward    启动端口转发GUI工具")


def _launch_port_forward():
    try:
        from multi_system.gui import launch_port_forward_gui

        launch_port_forward_gui()
    except ImportError:
        print("错误: 需要安装PySide6才能使用GUI功能")
        print("请运行: pip install multi-system[gui]")
        sys.exit(1)


if __name__ == "__main__":
    main()
