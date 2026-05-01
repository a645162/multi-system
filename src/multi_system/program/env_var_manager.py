"""环境变量可视化管理"""
import os
from dataclasses import dataclass


@dataclass
class EnvVarEntry:
    name: str
    value: str
    source: str  # "process" / "shell_rc" / "registry"


class EnvVarManager:
    @staticmethod
    def list_vars() -> list[EnvVarEntry]:
        return [EnvVarEntry(k, v, "process") for k, v in sorted(os.environ.items())]

    @staticmethod
    def search(keyword: str) -> list[EnvVarEntry]:
        kw = keyword.lower()
        return [
            e
            for e in EnvVarManager.list_vars()
            if kw in e.name.lower() or kw in e.value.lower()
        ]

    @staticmethod
    def set_var(name: str, value: str) -> None:
        os.environ[name] = value

    @staticmethod
    def delete_var(name: str) -> None:
        os.environ.pop(name, None)
