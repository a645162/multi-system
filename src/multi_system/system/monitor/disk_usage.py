"""
磁盘空间分析
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DirInfo:
    path: str
    size: int
    file_count: int


@dataclass
class BigFile:
    path: str
    size: int


class DiskUsageAnalyzer:
    @staticmethod
    def scan_directory(path: Path, top_n: int = 50) -> list[DirInfo]:
        dirs = []
        try:
            for entry in os.scandir(path):
                if entry.is_dir(follow_symlinks=False):
                    try:
                        total_size = 0
                        file_count = 0
                        for root, _, files in os.walk(entry.path, onerror=lambda e: None):
                            for f in files:
                                try:
                                    total_size += os.path.getsize(os.path.join(root, f))
                                    file_count += 1
                                except (OSError, PermissionError):
                                    continue
                        dirs.append(DirInfo(entry.path, total_size, file_count))
                    except PermissionError:
                        continue
        except PermissionError:
            return []
        dirs.sort(key=lambda d: d.size, reverse=True)
        return dirs[:top_n]

    @staticmethod
    def find_big_files(path: Path, min_size_mb: int = 100, limit: int = 50) -> list[BigFile]:
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
        files.sort(key=lambda f: f.size, reverse=True)
        return files[:limit]
