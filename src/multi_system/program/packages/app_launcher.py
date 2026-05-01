"""应用启动器"""
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppEntry:
    name: str
    command: str
    icon: str = ""


class AppLauncher:
    @staticmethod
    def list_apps() -> list[AppEntry]:
        if sys.platform == "linux":
            return AppLauncher._list_linux()
        elif sys.platform == "darwin":
            return AppLauncher._list_macos()
        return []

    @staticmethod
    def _list_linux() -> list[AppEntry]:
        apps = []
        dirs = [
            Path("/usr/share/applications"),
            Path.home() / ".local" / "share" / "applications",
        ]
        for d in dirs:
            if not d.exists():
                continue
            for f in d.glob("*.desktop"):
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                    name = cmd = icon = ""
                    nolaunch = False
                    for line in content.splitlines():
                        if line.startswith("Name="):
                            name = line.split("=", 1)[1].strip()
                        elif line.startswith("Exec="):
                            cmd = line.split("=", 1)[1].strip()
                        elif line.startswith("Icon="):
                            icon = line.split("=", 1)[1].strip()
                        elif line.startswith("NoDisplay="):
                            nolaunch = (
                                line.split("=", 1)[1].strip().lower() == "true"
                            )
                    if name and cmd and not nolaunch:
                        apps.append(AppEntry(name, cmd, icon))
                except OSError:
                    continue
        return sorted(apps, key=lambda a: a.name.lower())

    @staticmethod
    def _list_macos() -> list[AppEntry]:
        apps = []
        app_dir = Path("/Applications")
        if app_dir.exists():
            for f in app_dir.iterdir():
                if f.suffix == ".app":
                    apps.append(AppEntry(f.stem, f"open '{f}'"))
        return sorted(apps, key=lambda a: a.name.lower())

    @staticmethod
    def launch(command: str) -> bool:
        try:
            subprocess.Popen(command.split(), start_new_session=True)
            return True
        except (FileNotFoundError, OSError):
            return False
