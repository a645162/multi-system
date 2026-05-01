import sys

from multi_system.gui.registry import get_all, get_by_cli


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        _print_help()
        return

    cmd = args[0]
    feat = get_by_cli(cmd)
    if feat is None:
        print(f"未知命令: {cmd}")
        print("使用 --help 查看可用命令")
        sys.exit(1)

    _dispatch(feat.id)


def _print_help():
    print("Usage: multi-system <command>")
    print()
    print("Commands:")
    for feat in get_all():
        print(f"  {feat.cli_name:<20} {feat.description}")
    print()
    print("GUI入口: multi-system-gui [command]")


def _dispatch(feature_id: str):
    try:
        from multi_system.gui import launch_feature_gui
        launch_feature_gui(feature_id)
    except ImportError as e:
        print(f"错误: {e}")
        print("请运行: pip install multi-system[gui]")
        sys.exit(1)


if __name__ == "__main__":
    main()
