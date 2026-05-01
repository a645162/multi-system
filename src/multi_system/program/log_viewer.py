"""日志查看器"""
from pathlib import Path


class LogViewer:
    COMMON_LOGS = {
        "linux": ["/var/log/syslog", "/var/log/auth.log", "/var/log/kern.log"],
        "darwin": ["/var/log/system.log", "/var/log/secure.log"],
        "win32": [],
    }

    @staticmethod
    def get_common_logs() -> list[Path]:
        import sys

        return [
            Path(p)
            for p in LogViewer.COMMON_LOGS.get(sys.platform, [])
            if Path(p).exists()
        ]

    @staticmethod
    def read_tail(path: Path, lines: int = 200) -> str:
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            return "\n".join(content.splitlines()[-lines:])
        except (OSError, PermissionError):
            return ""

    @staticmethod
    def search(path: Path, keyword: str, max_lines: int = 500) -> list[str]:
        try:
            result = []
            with open(path, encoding="utf-8", errors="replace") as f:
                for _i, line in enumerate(f):
                    if keyword.lower() in line.lower():
                        result.append(line.rstrip())
                        if len(result) >= max_lines:
                            break
            return result
        except (OSError, PermissionError):
            return []
