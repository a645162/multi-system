"""批量重命名"""
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RenameOp:
    old_path: Path
    new_path: Path


def preview_rename(
    directory: Path, pattern: str, replacement: str, regex: bool = False
) -> list[RenameOp]:
    ops = []
    for f in sorted(directory.iterdir()):
        if not f.is_file():
            continue
        name = f.name
        if regex:
            new_name = re.sub(pattern, replacement, name)
        else:
            new_name = name.replace(pattern, replacement)
        if new_name != name:
            ops.append(RenameOp(f, f.parent / new_name))
    return ops


def execute_rename(ops: list[RenameOp]) -> int:
    success = 0
    for op in ops:
        try:
            op.old_path.rename(op.new_path)
            success += 1
        except OSError:
            continue
    return success
