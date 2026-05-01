"""
数据目录管理与TOML/YAML读写
"""

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # ty: ignore[unresolved-import]
    except ImportError:
        tomllib: Any = None

try:
    import tomli_w
except ImportError:
    tomli_w: Any = None

try:
    import yaml
except ImportError:
    yaml: Any = None


class DataManager:
    def __init__(self, base_dir: Path | None = None):
        self._base_dir = base_dir or Path.cwd() / "data"

    def get_data_dir(self, feature: str = "") -> Path:
        """返回 data/{feature}/ 目录，自动创建"""
        path = self._base_dir / feature if feature else self._base_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def load_toml(self, path: Path) -> dict[str, Any]:
        """读取TOML文件，不存在返回空dict"""
        if not path.exists():
            return {}
        if tomllib is None:
            raise ImportError("需要安装 tomli (Python 3.10) 或使用 Python 3.11+")
        with open(path, "rb") as f:
            return tomllib.load(f)

    def save_toml(self, path: Path, data: dict[str, Any]) -> None:
        """写入TOML文件"""
        if tomli_w is None:
            raise ImportError("需要安装 tomli_w")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            tomli_w.dump(data, f)

    def load_yaml(self, path: Path) -> dict[str, Any]:
        """读取YAML文件，不存在返回空dict"""
        if not path.exists():
            return {}
        if yaml is None:
            raise ImportError("需要安装 pyyaml")
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def save_yaml(self, path: Path, data: dict[str, Any]) -> None:
        """写入YAML文件"""
        if yaml is None:
            raise ImportError("需要安装 pyyaml")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
