"""
跨平台路径工具模块
"""

from .paths import (
    get_cache_dir,
    get_config_dir,
    get_data_dir,
    get_desktop,
    get_documents,
    get_downloads,
    get_home,
    get_shell_rc_path,
    get_temp_dir,
    get_all_common_paths,
)

__all__ = [
    "get_home",
    "get_desktop",
    "get_downloads",
    "get_documents",
    "get_config_dir",
    "get_data_dir",
    "get_cache_dir",
    "get_temp_dir",
    "get_shell_rc_path",
    "get_all_common_paths",
]
