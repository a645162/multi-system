"""
跨平台常用路径工具
"""

import os
import sys
from pathlib import Path


def get_home() -> Path:
    return Path.home()


def get_desktop() -> Path:
    home = get_home()
    if sys.platform == "win32":
        return home / "Desktop"
    if sys.platform == "darwin":
        return home / "Desktop"
    xdg = os.environ.get("XDG_DESKTOP_DIR")
    if xdg:
        return Path(xdg)
    return home / "Desktop"


def get_downloads() -> Path:
    home = get_home()
    if sys.platform == "win32":
        return home / "Downloads"
    if sys.platform == "darwin":
        return home / "Downloads"
    xdg = os.environ.get("XDG_DOWNLOAD_DIR")
    if xdg:
        return Path(xdg)
    return home / "Downloads"


def get_documents() -> Path:
    home = get_home()
    if sys.platform == "win32":
        import ctypes.wintypes
        csidl = 5  # CSIDL_MY_DOCUMENTS
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf)
        return Path(buf.value)
    if sys.platform == "darwin":
        return home / "Documents"
    xdg = os.environ.get("XDG_DOCUMENTS_DIR")
    if xdg:
        return Path(xdg)
    return home / "Documents"


def get_config_dir(app_name: str = "") -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", get_home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = get_home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", get_home() / ".config"))
    return base / app_name if app_name else base


def get_data_dir(app_name: str = "") -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", get_home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = get_home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", get_home() / ".local" / "share"))
    return base / app_name if app_name else base


def get_cache_dir(app_name: str = "") -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", get_home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = get_home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", get_home() / ".cache"))
    return base / app_name if app_name else base


def get_temp_dir() -> Path:
    return Path(os.environ.get("TEMP" if sys.platform == "win32" else "TMPDIR", "/tmp"))


def get_shell_rc_path(shell: str = "") -> Path:
    """返回 shell rc 文件路径 (如 .bashrc, .zshrc)"""
    home = get_home()
    if not shell:
        shell = os.environ.get("SHELL", "/bin/bash").split("/")[-1]
    rc_map = {
        "bash": home / ".bashrc",
        "zsh": home / ".zshrc",
        "fish": get_config_dir("fish") / "config.fish",
    }
    return rc_map.get(shell, home / f".{shell}rc")


def get_all_common_paths() -> dict[str, Path]:
    """返回所有常用路径的字典"""
    return {
        "home": get_home(),
        "desktop": get_desktop(),
        "downloads": get_downloads(),
        "documents": get_documents(),
        "config": get_config_dir(),
        "data": get_data_dir(),
        "cache": get_cache_dir(),
        "temp": get_temp_dir(),
    }
