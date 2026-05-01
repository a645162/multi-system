"""
Shell Alias 解析与写入
"""

import re
from dataclasses import dataclass

from multi_system.system.shells.shell_base import RCFileManager


@dataclass
class AliasEntry:
    name: str
    command: str
    line_number: int = 0


_ALIAS_RE = re.compile(r"""^alias\s+([^=]+?)=(['"]?)(.+?)\2\s*$""")


class AliasManager:
    def __init__(self, shell: str):
        self._rc = RCFileManager(shell)
        self.shell = shell

    def list_aliases(self) -> list[AliasEntry]:
        content = self._rc.read_rc()
        aliases = []
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            m = _ALIAS_RE.match(stripped)
            if m:
                aliases.append(AliasEntry(
                    name=m.group(1).strip(),
                    command=m.group(3),
                    line_number=i,
                ))
        return aliases

    def add_alias(self, name: str, command: str) -> None:
        content = self._rc.read_rc()
        entry = f'\nalias {name}="{command}"\n'
        if content and not content.endswith("\n"):
            entry = "\n" + entry
        content += entry
        self._rc.write_rc(content)

    def remove_alias(self, name: str) -> bool:
        content = self._rc.read_rc()
        lines = content.splitlines(keepends=True)
        pattern = re.compile(rf"^alias\s+{re.escape(name)}\s*=")
        new_lines = [l for l in lines if not pattern.match(l.strip())]
        if len(new_lines) == len(lines):
            return False
        self._rc.write_rc("".join(new_lines))
        return True

    def update_alias(self, name: str, command: str) -> bool:
        content = self._rc.read_rc()
        lines = content.splitlines(keepends=True)
        pattern = re.compile(rf"^alias\s+{re.escape(name)}\s*=")
        found = False
        for i, line in enumerate(lines):
            if pattern.match(line.strip()):
                lines[i] = f'alias {name}="{command}"\n'
                found = True
                break
        if not found:
            return False
        self._rc.write_rc("".join(lines))
        return True
