import os
import sys
import platform
import subprocess
import ctypes
from pathlib import Path
from typing import Union, Tuple, Optional


def get_os_type() -> str:
    """
    检测当前操作系统类型

    Returns:
        str: 'windows', 'macos', 'linux' 或 'unknown'
    """
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"


def is_symlink(path: Union[str, Path]) -> bool:
    """
    检测指定路径是否为软连接

    Args:
        path: 要检测的路径

    Returns:
        bool: 如果是软连接返回True，否则返回False
    """
    path = Path(path)
    return path.is_symlink()


def get_symlink_target(path: Union[str, Path]) -> Optional[Path]:
    """
    获取软连接的目标路径

    Args:
        path: 软连接路径

    Returns:
        Optional[Path]: 如果是软连接则返回目标路径，否则返回None
    """
    path = Path(path)
    if path.is_symlink():
        return path.resolve()
    return None


def is_admin() -> bool:
    """
    检查当前进程是否拥有管理员权限

    Returns:
        bool: 如果是管理员权限返回True，否则返回False
    """
    os_type = get_os_type()

    if os_type == "windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    elif os_type in ("macos", "linux"):
        # Unix系统检查是否为root
        return os.geteuid() == 0
    return False


def run_as_admin(args=None):
    """
    以管理员权限重新运行当前脚本

    Args:
        args: 运行参数列表，默认为sys.argv

    Returns:
        None: 此函数会启动一个新的进程并退出当前进程
    """
    if args is None:
        args = sys.argv

    os_type = get_os_type()

    if os_type == "windows":
        script = args[0]
        params = " ".join([f'"{arg}"' for arg in args[1:]])

        # 使用Windows的ShellExecute以管理员权限运行
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
    elif os_type == "macos":
        # 使用osascript请求权限
        script = args[0]
        params = " ".join([f'"{arg}"' for arg in args[1:]])
        os.system(
            f"osascript -e 'do shell script \"python3 {script} {params}\" with administrator privileges'"
        )
    elif os_type == "linux":
        # 使用sudo请求权限
        script = args[0]
        params = " ".join([f'"{arg}"' for arg in args[1:]])
        os.system(f"sudo python3 {script} {params}")

    # 退出当前的非管理员进程
    sys.exit(0)


def create_symlink_windows(
    source: Union[str, Path],
    target: Union[str, Path],
    is_dir: bool = False,
    auto_elevate: bool = True,
) -> Tuple[bool, str]:
    """
    在Windows上创建软连接

    Args:
        source: 源文件/目录路径
        target: 目标链接路径
        is_dir: 是否为目录
        auto_elevate: 是否自动请求管理员权限

    Returns:
        Tuple[bool, str]: (成功标志, 消息)
    """
    source = Path(source).resolve()
    target = Path(target).resolve()

    # 检查源是否存在
    if not source.exists():
        return False, f"源路径不存在: {source}"

    # 检查目标位置是否已存在
    if target.exists():
        if is_symlink(target):
            existing_target = get_symlink_target(target)
            if existing_target == source:
                return True, f"软连接已存在且指向正确目标: {source}"
            else:
                return False, f"目标位置已存在指向其他位置的软连接: {existing_target}"
        else:
            return False, f"目标位置已存在非软连接文件/目录: {target}"

    # 确保目标父目录存在
    target.parent.mkdir(parents=True, exist_ok=True)

    # 检查权限并自动提升
    if auto_elevate and not is_admin():
        # 设置环境变量以传递参数
        os.environ["SYMLINK_SOURCE"] = str(source)
        os.environ["SYMLINK_TARGET"] = str(target)
        os.environ["SYMLINK_IS_DIR"] = "1" if is_dir else "0"

        print("需要管理员权限创建软连接，正在请求提升权限...")
        run_as_admin()
        # 如果代码运行到这里，说明提权失败或用户取消
        return False, "权限提升失败或用户取消操作"

    # 创建软连接
    try:
        cmd = ["cmd", "/c", "mklink"]
        if is_dir:
            cmd.append("/d")
        cmd.append(str(target))
        cmd.append(str(source))

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"创建软连接失败: {result.stderr.strip()}"
        return True, "软连接创建成功"
    except Exception as e:
        return False, f"创建软连接时出错: {str(e)}"


def create_symlink_unix(
    source: Union[str, Path], target: Union[str, Path], auto_elevate: bool = True
) -> Tuple[bool, str]:
    """
    在Unix系统(MacOS/Linux)上创建软连接

    Args:
        source: 源文件/目录路径
        target: 目标链接路径
        auto_elevate: 是否自动请求权限提升

    Returns:
        Tuple[bool, str]: (成功标志, 消息)
    """
    source = Path(source).resolve()
    target = Path(target).resolve()

    # 检查源是否存在
    if not source.exists():
        return False, f"源路径不存在: {source}"

    # 检查目标位置是否已存在
    if target.exists():
        if is_symlink(target):
            existing_target = get_symlink_target(target)
            if existing_target == source:
                return True, f"软连接已存在且指向正确目标: {source}"
            else:
                return False, f"目标位置已存在指向其他位置的软连接: {existing_target}"
        else:
            return False, f"目标位置已存在非软连接文件/目录: {target}"

    # 确保目标父目录存在
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        if auto_elevate:
            # 设置环境变量以传递参数
            os.environ["SYMLINK_SOURCE"] = str(source)
            os.environ["SYMLINK_TARGET"] = str(target)

            print("需要管理员权限创建目录或软连接，正在请求提升权限...")
            run_as_admin()
            # 如果代码运行到这里，说明提权失败或用户取消
            return False, "权限提升失败或用户取消操作"
        else:
            return False, f"没有创建目录的权限: {target.parent}"

    # 创建软连接
    try:
        target.symlink_to(source)
        return True, "软连接创建成功"
    except PermissionError:
        if auto_elevate:
            # 设置环境变量以传递参数
            os.environ["SYMLINK_SOURCE"] = str(source)
            os.environ["SYMLINK_TARGET"] = str(target)

            print("需要管理员权限创建软连接，正在请求提升权限...")
            run_as_admin()
            # 如果代码运行到这里，说明提权失败或用户取消
            return False, "权限提升失败或用户取消操作"
        else:
            return False, "没有创建软连接的权限"
    except Exception as e:
        return False, f"创建软连接时出错: {str(e)}"


def create_symlink(
    source: Union[str, Path],
    target: Union[str, Path],
    is_dir: bool = None,
    auto_elevate: bool = True,
) -> Tuple[bool, str]:
    """
    根据当前操作系统创建软连接

    Args:
        source: 源文件/目录路径
        target: 目标链接路径
        is_dir: 是否为目录 (仅Windows需要，其他系统会自动判断)
        auto_elevate: 是否自动请求权限提升

    Returns:
        Tuple[bool, str]: (成功标志, 消息)
    """
    # 检查环境变量中是否有参数（从权限提升后传递过来的）
    if "SYMLINK_SOURCE" in os.environ and "SYMLINK_TARGET" in os.environ:
        source = os.environ.pop("SYMLINK_SOURCE")
        target = os.environ.pop("SYMLINK_TARGET")
        if "SYMLINK_IS_DIR" in os.environ:
            is_dir = os.environ.pop("SYMLINK_IS_DIR") == "1"

    source = Path(source)
    target = Path(target)

    # 自动判断是否为目录
    if is_dir is None:
        is_dir = source.is_dir()

    os_type = get_os_type()

    if os_type == "windows":
        return create_symlink_windows(source, target, is_dir, auto_elevate)
    elif os_type in ("macos", "linux"):
        return create_symlink_unix(source, target, auto_elevate)
    else:
        return False, f"不支持的操作系统: {platform.system()}"


if __name__ == "__main__":
    # 测试代码
    source_path = Path("test_source")
    target_path = Path("test_link")

    # 创建测试目录
    source_path.mkdir(exist_ok=True)

    # 创建软连接
    success, message = create_symlink(source_path, target_path)
    print(f"创建结果: {success}, {message}")

    # 检测软连接
    if is_symlink(target_path):
        print(f"成功创建软连接，目标为: {get_symlink_target(target_path)}")
