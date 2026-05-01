"""
Shell检测与RC文件管理基础工具
"""

import os
import shutil
from datetime import datetime
from difflib import unified_diff
from pathlib import Path

from multi_system.path.paths import get_data_dir, get_home, get_shell_rc_path


class ShellDetector:
    SUPPORTED = ("bash", "zsh", "fish")

    @staticmethod
    def detect() -> str:
        shell_path = os.environ.get("SHELL", "/bin/bash")
        name = shell_path.split("/")[-1]
        return name if name in ShellDetector.SUPPORTED else "bash"

    @staticmethod
    def get_rc_path(shell: str) -> Path:
        return get_shell_rc_path(shell)

    @staticmethod
    def get_history_path(shell: str) -> Path:
        home = get_home()
        if shell == "zsh":
            return home / ".zsh_history"
        if shell == "fish":
            return get_data_dir("fish") / "fish_history"
        return home / ".bash_history"


class RCFileManager:
    BACKUP_MARKER = "# Added by MultiSystem"

    def __init__(self, shell: str, backup_dir: Path | None = None):
        self.shell = shell
        self.rc_path = ShellDetector.get_rc_path(shell)
        self._backup_dir = backup_dir or get_data_dir("shell") / "backups"

    def read_rc(self) -> str:
        if not self.rc_path.exists():
            return ""
        return self.rc_path.read_text(encoding="utf-8")

    def write_rc(self, content: str) -> None:
        self.rc_path.write_text(content, encoding="utf-8")

    def backup(self, tag: str = "") -> Path:
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"{self.shell}_{ts}"
        if tag:
            name += f"_{tag}"
        dest = self._backup_dir / f"{name}.bak"
        shutil.copy2(self.rc_path, dest)
        return dest

    def list_backups(self) -> list[Path]:
        if not self._backup_dir.exists():
            return []
        return sorted(
            p for p in self._backup_dir.iterdir()
            if p.name.startswith(self.shell) and p.suffix == ".bak"
        )

    def restore(self, backup_path: Path) -> None:
        shutil.copy2(backup_path, self.rc_path)

    def diff(self, backup_path: Path) -> list[str]:
        current = self.read_rc().splitlines(keepends=True)
        old = backup_path.read_text(encoding="utf-8").splitlines(keepends=True)
        return list(unified_diff(
            old, current,
            fromfile=backup_path.name, tofile=self.rc_path.name,
        ))
