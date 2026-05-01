import os
import platform
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, Union

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_system_type() -> str:
    """
    获取当前操作系统类型

    Returns:
        str: "Windows", "Darwin" (macOS) 或 "Linux"
    """
    return platform.system()


def get_env_var(var_name: str) -> Optional[str]:
    """
    获取环境变量值

    Args:
        var_name: 环境变量名

    Returns:
        Optional[str]: 环境变量的值，如不存在则返回 None
    """
    return os.environ.get(var_name)


def get_all_env_vars() -> Dict[str, str]:
    """
    获取所有环境变量

    Returns:
        Dict[str, str]: 所有环境变量的字典
    """
    return dict(os.environ)


def set_env_var_windows(
    var_name: str, var_value: str, system_wide: bool = False
) -> bool:
    """
    在 Windows 系统中设置环境变量

    Args:
        var_name: 环境变量名
        var_value: 环境变量值
        system_wide: 是否设置为系统环境变量，默认为用户环境变量

    Returns:
        bool: 设置是否成功
    """
    try:
        import winreg

        # 确定注册表路径
        if system_wide:
            key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            reg_type = winreg.HKEY_LOCAL_MACHINE
        else:
            key_path = r"Environment"
            reg_type = winreg.HKEY_CURRENT_USER

        # 打开注册表项
        with winreg.OpenKey(reg_type, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.SetValueEx(key, var_name, 0, winreg.REG_SZ, var_value)

        # 广播环境变量更改消息
        subprocess.call(["setx", var_name, var_value])

        # 也在当前进程中设置环境变量
        os.environ[var_name] = var_value
        return True
    except Exception as e:
        logger.error(f"Windows 环境变量设置失败: {e}")
        return False


def set_env_var_macos(var_name: str, var_value: str) -> bool:
    """
    在 macOS 系统中设置环境变量（配置 zsh）

    Args:
        var_name: 环境变量名
        var_value: 环境变量值

    Returns:
        bool: 设置是否成功
    """
    try:
        zshrc_path = os.path.expanduser("~/.zshrc")

        # 读取现有文件内容
        content = ""
        if os.path.exists(zshrc_path):
            with open(zshrc_path, "r") as file:
                content = file.read()

        # 构建环境变量导出语句
        export_statement = f'export {var_name}="{var_value}"'

        # 检查是否已存在该环境变量设置
        if f"export {var_name}=" in content:
            # 替换现有设置
            new_lines = []
            for line in content.split("\n"):
                if f"export {var_name}=" in line:
                    new_lines.append(export_statement)
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)
        else:
            # 添加新设置到文件末尾
            if content and not content.endswith("\n"):
                content += "\n"
            content += f"\n# Added by LLMsClientConfig\n{export_statement}\n"

        # 写回文件
        with open(zshrc_path, "w") as file:
            file.write(content)

        # 当前进程中设置环境变量
        os.environ[var_name] = var_value
        logger.info("环境变量已添加到 ~/.zshrc，请运行 'source ~/.zshrc' 使其生效")
        return True
    except Exception as e:
        logger.error(f"macOS 环境变量设置失败: {e}")
        return False


def set_env_var_linux(var_name: str, var_value: str) -> bool:
    """
    在 Linux 系统中设置环境变量（配置 bash）

    Args:
        var_name: 环境变量名
        var_value: 环境变量值

    Returns:
        bool: 设置是否成功
    """
    try:
        bashrc_path = os.path.expanduser("~/.bashrc")

        # 读取现有文件内容
        content = ""
        if os.path.exists(bashrc_path):
            with open(bashrc_path, "r") as file:
                content = file.read()

        # 构建环境变量导出语句
        export_statement = f'export {var_name}="{var_value}"'

        # 检查是否已存在该环境变量设置
        if f"export {var_name}=" in content:
            # 替换现有设置
            new_lines = []
            for line in content.split("\n"):
                if f"export {var_name}=" in line:
                    new_lines.append(export_statement)
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)
        else:
            # 添加新设置到文件末尾
            if content and not content.endswith("\n"):
                content += "\n"
            content += f"\n# Added by LLMsClientConfig\n{export_statement}\n"

        # 写回文件
        with open(bashrc_path, "w") as file:
            file.write(content)

        # 当前进程中设置环境变量
        os.environ[var_name] = var_value
        logger.info("环境变量已添加到 ~/.bashrc，请运行 'source ~/.bashrc' 使其生效")
        return True
    except Exception as e:
        logger.error(f"Linux 环境变量设置失败: {e}")
        return False


def set_env_var(var_name: str, var_value: str, system_wide: bool = False) -> bool:
    """
    根据操作系统类型设置环境变量

    Args:
        var_name: 环境变量名
        var_value: 环境变量值
        system_wide: 在Windows系统上是否设置为系统环境变量（默认为用户环境变量）

    Returns:
        bool: 设置是否成功
    """
    system = get_system_type()

    if system == "Windows":
        return set_env_var_windows(var_name, var_value, system_wide)
    elif system == "Darwin":  # macOS
        return set_env_var_macos(var_name, var_value)
    elif system == "Linux":
        return set_env_var_linux(var_name, var_value)
    else:
        logger.error(f"不支持的操作系统: {system}")
        return False


def remove_env_var(var_name: str, system_wide: bool = False) -> bool:
    """
    根据操作系统类型移除环境变量

    Args:
        var_name: 要移除的环境变量名
        system_wide: 在Windows系统上是否移除系统环境变量（默认为用户环境变量）

    Returns:
        bool: 移除是否成功
    """
    system = get_system_type()

    try:
        if system == "Windows":
            import winreg

            # 确定注册表路径
            if system_wide:
                key_path = (
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                )
                reg_type = winreg.HKEY_LOCAL_MACHINE
            else:
                key_path = r"Environment"
                reg_type = winreg.HKEY_CURRENT_USER

            # 打开注册表项
            with winreg.OpenKey(reg_type, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                try:
                    winreg.DeleteValue(key, var_name)
                    subprocess.call(
                        [
                            "REG",
                            "delete",
                            f"{reg_type}\\{key_path}",
                            "/v",
                            var_name,
                            "/f",
                        ]
                    )
                except FileNotFoundError:
                    logger.warning(f"环境变量 {var_name} 不存在")

        elif system == "Darwin":  # macOS
            zshrc_path = os.path.expanduser("~/.zshrc")
            if os.path.exists(zshrc_path):
                with open(zshrc_path, "r") as file:
                    content = file.read()

                new_lines = []
                skip_next = False
                for line in content.split("\n"):
                    if skip_next:
                        skip_next = False
                        continue

                    if (
                        "# Added by LLMsClientConfig" in line
                        and line.strip() == "# Added by LLMsClientConfig"
                    ):
                        # TODO: next_line 变量未使用
                        # next_line = f"export {var_name}="
                        skip_next = True
                        continue

                    if f"export {var_name}=" not in line:
                        new_lines.append(line)

                with open(zshrc_path, "w") as file:
                    file.write("\n".join(new_lines))

                logger.info(
                    "环境变量已从 ~/.zshrc 移除，请运行 'source ~/.zshrc' 使其生效"
                )

        elif system == "Linux":
            bashrc_path = os.path.expanduser("~/.bashrc")
            if os.path.exists(bashrc_path):
                with open(bashrc_path, "r") as file:
                    content = file.read()

                new_lines = []
                skip_next = False
                for line in content.split("\n"):
                    if skip_next:
                        skip_next = False
                        continue

                    if (
                        "# Added by LLMsClientConfig" in line
                        and line.strip() == "# Added by LLMsClientConfig"
                    ):
                        # TODO: next_line 变量未使用
                        # next_line = f"export {var_name}="
                        skip_next = True
                        continue

                    if f"export {var_name}=" not in line:
                        new_lines.append(line)

                with open(bashrc_path, "w") as file:
                    file.write("\n".join(new_lines))

                logger.info(
                    "环境变量已从 ~/.bashrc 移除，请运行 'source ~/.bashrc' 使其生效"
                )

        # 从当前进程中移除环境变量
        if var_name in os.environ:
            del os.environ[var_name]

        return True
    except Exception as e:
        logger.error(f"移除环境变量失败: {e}")
        return False


def append_to_path(new_path: Union[str, Path]) -> bool:
    """
    将路径添加到 PATH 环境变量

    Args:
        new_path: 要添加的路径

    Returns:
        bool: 添加是否成功
    """
    new_path_str = str(new_path)
    path_var = os.environ.get("PATH", "")
    path_separator = ";" if get_system_type() == "Windows" else ":"
    paths = path_var.split(path_separator)

    # 检查路径是否已存在
    if new_path_str in paths:
        logger.info(f"路径 '{new_path_str}' 已在 PATH 中")
        return True

    # 添加到 PATH
    new_path_value = (
        path_var + path_separator + new_path_str if path_var else new_path_str
    )
    return set_env_var("PATH", new_path_value)


def remove_from_path(path_to_remove: Union[str, Path]) -> bool:
    """
    从 PATH 环境变量中移除路径

    Args:
        path_to_remove: 要移除的路径

    Returns:
        bool: 移除是否成功
    """
    path_to_remove_str = str(path_to_remove)
    path_var = os.environ.get("PATH", "")
    path_separator = ";" if get_system_type() == "Windows" else ":"
    paths = path_var.split(path_separator)

    # 移除路径（如存在）
    if path_to_remove_str in paths:
        paths.remove(path_to_remove_str)
        new_path_value = path_separator.join(paths)
        return set_env_var("PATH", new_path_value)
    else:
        logger.info(f"路径 '{path_to_remove_str}' 不在 PATH 中")
        return True
