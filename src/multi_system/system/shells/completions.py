"""
Shell 补全脚本管理
"""

import os
from dataclasses import dataclass
from pathlib import Path

from multi_system.path.paths import get_config_dir, get_data_dir, get_home


@dataclass
class CompletionEntry:
    name: str
    path: Path
    size: int


class CompletionManager:
    def __init__(self, shell: str):
        self.shell = shell

    def list_completions(self) -> list[CompletionEntry]:
        dirs = self._get_completion_dirs()
        entries = []
        seen = set()
        for d in dirs:
            if not d.exists():
                continue
            for p in sorted(d.iterdir()):
                if p.is_file() and p.name not in seen:
                    seen.add(p.name)
                    entries.append(CompletionEntry(
                        name=p.name,
                        path=p,
                        size=p.stat().st_size,
                    ))
        return entries

    def _get_completion_dirs(self) -> list[Path]:
        if self.shell == "bash":
            return [
                Path("/etc/bash_completion.d"),
                Path("/usr/share/bash-completion/completions"),
                get_data_dir("bash-completion"),
                get_home() / ".local" / "share" / "bash-completion" / "completions",
            ]
        if self.shell == "zsh":
            zsh_comp = get_home() / ".zsh" / "completion"
            fpath_dirs = self._get_zsh_fpath()
            return [
                zsh_comp,
                Path("/usr/share/zsh/vendor-completions"),
                Path("/usr/local/share/zsh/site-functions"),
                *fpath_dirs,
            ]
        if self.shell == "fish":
            return [
                get_config_dir("fish") / "completions",
                Path("/usr/share/fish/vendor_completions.d"),
            ]
        return []

    def _get_zsh_fpath(self) -> list[Path]:
        rc = get_home() / ".zshrc"
        if not rc.exists():
            return []
        content = rc.read_text(encoding="utf-8")
        import re
        dirs = []
        for m in re.finditer(r"fpath\+=\s*(.+?)\s*$", content, re.MULTILINE):
            path_str = m.group(1).strip().strip("'\"")
            dirs.append(Path(path_str).expanduser())
        return dirs
