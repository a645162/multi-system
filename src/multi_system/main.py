import sys

_CLI_COMMANDS = {
    "port-forward": ("启动端口转发工具", "multi_system.gui", "launch_port_forward_gui"),
}


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        _print_help()
        return

    cmd = args[0]
    if cmd not in _CLI_COMMANDS:
        print(f"未知命令: {cmd}")
        print("使用 --help 查看可用命令")
        sys.exit(1)

    _dispatch(cmd)


def _print_help():
    print("Usage: multi-system <command>")
    print()
    print("Commands:")
    for cmd, (desc, *_) in _CLI_COMMANDS.items():
        print(f"  {cmd:<16} {desc}")
    print()
    print("GUI入口: multi-system-gui <command>")


def _dispatch(cmd: str):
    _, module_name, func_name = _CLI_COMMANDS[cmd]
    try:
        import importlib
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        func()
    except ImportError as e:
        print(f"错误: {e}")
        print("请运行: pip install multi-system[gui]")
        sys.exit(1)


if __name__ == "__main__":
    main()
