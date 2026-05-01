"""
RC 文件配置管理（备份/恢复/对比）
"""

from pathlib import Path

from multi_system.system.shells.shell_base import RCFileManager


class RCManager:
    def __init__(self, shell: str):
        self._rc = RCFileManager(shell)
        self.shell = shell

    def backup(self, tag: str = "") -> Path:
        return self._rc.backup(tag)

    def list_backups(self) -> list[dict]:
        backups = []
        for p in self._rc.list_backups():
            stat = p.stat()
            backups.append({
                "path": p,
                "name": p.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
            })
        return backups

    def restore(self, backup_path: Path) -> None:
        self._rc.restore(backup_path)

    def diff(self, backup_path: Path) -> list[str]:
        return self._rc.diff(backup_path)

    def read_current(self) -> str:
        return self._rc.read_rc()

    def read_backup(self, backup_path: Path) -> str:
        return backup_path.read_text(encoding="utf-8")
