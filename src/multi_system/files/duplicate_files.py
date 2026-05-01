"""重复文件查找"""
import hashlib
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DuplicateGroup:
    hash: str
    size: int
    paths: list[str]


def find_duplicates(path: Path, min_size: int = 1024) -> list[DuplicateGroup]:
    size_map: dict[int, list[str]] = defaultdict(list)
    for root, _, filenames in os.walk(path, onerror=lambda e: None):
        for f in filenames:
            try:
                full = os.path.join(root, f)
                size = os.path.getsize(full)
                if size >= min_size:
                    size_map[size].append(full)
            except (OSError, PermissionError):
                continue

    hash_map: dict[str, list[str]] = defaultdict(list)
    for _size, paths in size_map.items():
        if len(paths) < 2:
            continue
        for p in paths:
            try:
                with open(p, "rb") as f:
                    h = hashlib.md5(f.read()).hexdigest()
                hash_map[h].append(p)
            except (OSError, PermissionError):
                continue

    groups = []
    for h, paths in hash_map.items():
        if len(paths) >= 2:
            groups.append(
                DuplicateGroup(hash=h, size=os.path.getsize(paths[0]), paths=paths)
            )
    groups.sort(key=lambda g: g.size, reverse=True)
    return groups
