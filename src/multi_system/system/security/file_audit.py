"""文件权限审计"""
import os
import stat
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AuditIssue:
    path: str
    issue: str
    mode: str
    size: int


class FileAuditor:
    @staticmethod
    def scan(
        path: Path,
        check_world_writable: bool = True,
        check_suid: bool = True,
        limit: int = 200,
    ) -> list[AuditIssue]:
        issues = []
        for root, dirs, files in os.walk(path, onerror=lambda e: None):
            for name in files + dirs:
                full = os.path.join(root, name)
                try:
                    st = os.stat(full)
                    mode = st.st_mode
                    mode_str = stat.filemode(mode)
                    if check_world_writable and mode & stat.S_IWOTH:
                        issues.append(
                            AuditIssue(full, "World-writable", mode_str, st.st_size)
                        )
                    if check_suid and mode & stat.S_ISUID:
                        issues.append(
                            AuditIssue(full, "SUID bit set", mode_str, st.st_size)
                        )
                    if len(issues) >= limit:
                        return issues
                except (OSError, PermissionError):
                    continue
        return issues
