"""
Shell 历史记录解析与统计
"""

import re
from collections import Counter
from dataclasses import dataclass

from multi_system.system.shells.shell_base import ShellDetector


@dataclass
class HistoryStats:
    total: int
    unique: int
    top: list[tuple[str, int]]


class HistoryAnalyzer:
    def __init__(self, shell: str):
        self.shell = shell
        self.history_path = ShellDetector.get_history_path(shell)

    def parse(self) -> list[str]:
        if not self.history_path.exists():
            return []
        content = self.history_path.read_text(encoding="utf-8", errors="replace")
        if self.shell == "zsh":
            return self._parse_zsh(content)
        return self._parse_bash(content)

    @staticmethod
    def _parse_bash(content: str) -> list[str]:
        return [line.strip() for line in content.splitlines() if line.strip()]

    @staticmethod
    def _parse_zsh(content: str) -> list[str]:
        lines = []
        for line in content.splitlines():
            if line.startswith(": "):
                m = re.match(r"^: \d+:\d+;(.+)$", line)
                if m:
                    lines.append(m.group(1).strip())
            elif line.strip():
                lines.append(line.strip())
        return lines

    def stats(self, top_n: int = 20) -> HistoryStats:
        commands = self.parse()
        counter = Counter(commands)
        return HistoryStats(
            total=len(commands),
            unique=len(counter),
            top=counter.most_common(top_n),
        )

    def search(self, keyword: str) -> list[str]:
        return [cmd for cmd in self.parse() if keyword in cmd]
