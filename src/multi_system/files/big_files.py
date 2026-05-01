"""大文件扫描"""
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BigFile:
    path: str
    size: int


def find_big_files(path: Path, min_size_mb: int = 100, limit: int = 100) -> list[BigFile]:
    min_size = min_size_mb * 1024 * 1024
    files = []
    for root, _, filenames in os.walk(path, onerror=lambda e: None):
        for f in filenames:
            try:
                full = os.path.join(root, f)
                size = os.path.getsize(full)
                if size >= min_size:
                    files.append(BigFile(full, size))
            except (OSError, PermissionError):
                continue
    files.sort(key=lambda x: x.size, reverse=True)
    return files[:limit]
