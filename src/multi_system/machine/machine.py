import socket


def get_machine_name() -> str:
    """获取机器的机器名称"""
    return socket.gethostname()


def main():
    """主函数"""
    machine_name = get_machine_name()
    print(f"机器名称: {machine_name}")


if __name__ == "__main__":
    main()
