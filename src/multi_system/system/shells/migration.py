"""
Shell 配置迁移 (bash ↔ zsh)
"""

import re
from dataclasses import dataclass

from multi_system.system.shells.shell_base import RCFileManager


@dataclass
class MigrationEntry:
    category: str  # "alias" | "export" | "path" | "function"
    name: str
    value: str
    raw_line: str
    migratable: bool


class MigrationManager:
    def __init__(self, source_shell: str, target_shell: str):
        self._source = RCFileManager(source_shell)
        self._target = RCFileManager(target_shell)
        self.source_shell = source_shell
        self.target_shell = target_shell

    def analyze(self) -> list[MigrationEntry]:
        content = self._source.read_rc()
        entries = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            entry = self._parse_line(stripped)
            if entry:
                entries.append(entry)
        return entries

    def _parse_line(self, line: str) -> MigrationEntry | None:
        # alias
        m = re.match(r"^alias\s+([^=]+)=(['\"]?)(.+?)\2$", line)
        if m:
            return MigrationEntry("alias", m.group(1).strip(), m.group(3), line, True)

        # export
        m = re.match(r"^export\s+([A-Za-z_]\w*)=(.*)$", line)
        if m:
            return MigrationEntry("export", m.group(1), m.group(2), line, True)

        # PATH append
        m = re.match(r'^(?:export\s+)?PATH=["\']?\$PATH:([^"\']+)["\']?$', line)
        if m:
            return MigrationEntry("path", "PATH", m.group(1), line, True)

        # function
        m = re.match(r"^([A-Za-z_]\w*)\(\)\s*\{?$", line)
        if m:
            return MigrationEntry("function", m.group(1), "", line, False)

        return None

    def generate_migration(self, entries: list[MigrationEntry]) -> str:
        lines = [f"# Migrated from {self.source_shell} by MultiSystem"]
        for e in entries:
            if not e.migratable:
                continue
            if e.category == "alias":
                lines.append(f'alias {e.name}="{e.value}"')
            elif e.category == "export":
                lines.append(f"export {e.name}={e.value}")
            elif e.category == "path":
                lines.append(f'export PATH="$PATH:{e.value}"')
        return "\n".join(lines) + "\n"

    def execute(self, entries: list[MigrationEntry]) -> None:
        migration_text = self.generate_migration(entries)
        content = self._target.read_rc()
        if content and not content.endswith("\n"):
            content += "\n"
        content += "\n" + migration_text
        self._target.write_rc(content)
