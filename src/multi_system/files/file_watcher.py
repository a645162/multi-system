"""文件变更监控"""
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileEvent:
    path: str
    event_type: str  # "created" / "modified" / "deleted"


class SimpleFileWatcher:
    """简单的轮询式文件监控（跨平台兼容）"""

    def __init__(
        self,
        watch_dir: Path,
        callback: Callable[[FileEvent], None],
        interval: float = 2.0,
    ):
        self.watch_dir = watch_dir
        self.callback = callback
        self.interval = interval
        self._snapshot: dict[str, float] = {}
        self._running = False

    def _take_snapshot(self) -> dict[str, float]:
        snap = {}
        for root, _, files in os.walk(self.watch_dir, onerror=lambda e: None):
            for f in files:
                full = os.path.join(root, f)
                try:
                    snap[full] = os.path.getmtime(full)
                except OSError:
                    continue
        return snap

    def check_once(self) -> list[FileEvent]:
        new_snap = self._take_snapshot()
        events = []
        for path, mtime in new_snap.items():
            if path not in self._snapshot:
                events.append(FileEvent(path, "created"))
            elif self._snapshot[path] != mtime:
                events.append(FileEvent(path, "modified"))
        for path in self._snapshot:
            if path not in new_snap:
                events.append(FileEvent(path, "deleted"))
        self._snapshot = new_snap
        return events
