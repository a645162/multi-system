"""
开机启动项管理
"""

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StartupApp:
    name: str
    command: str
    enabled: bool
    source: str  # "systemd" / "launchd" / "registry" / "autostart"


class StartupAppManager:
    def list_apps(self) -> list[StartupApp]:
        if sys.platform == "linux":
            return self._list_linux()
        if sys.platform == "darwin":
            return self._list_macos()
        if sys.platform == "win32":
            return self._list_windows()
        return []

    def _list_linux(self) -> list[StartupApp]:
        apps = []
        systemd_dirs = [
            Path("/etc/systemd/system"),
            Path("/lib/systemd/system"),
            Path.home() / ".config" / "systemd" / "user",
        ]
        for d in systemd_dirs:
            if not d.exists():
                continue
            for f in d.iterdir():
                if f.suffix == ".service" and not f.is_symlink():
                    try:
                        content = f.read_text(encoding="utf-8", errors="replace")
                        desc = ""
                        for line in content.splitlines():
                            if line.startswith("Description="):
                                desc = line.split("=", 1)[1].strip()
                                break
                        apps.append(StartupApp(
                            name=desc or f.stem,
                            command=str(f),
                            enabled=not f.is_symlink(),
                            source="systemd",
                        ))
                    except (OSError, PermissionError):
                        continue

        autostart = Path.home() / ".config" / "autostart"
        if autostart.exists():
            for f in autostart.iterdir():
                if f.suffix == ".desktop":
                    try:
                        content = f.read_text(encoding="utf-8", errors="replace")
                        name = f.stem
                        exec_cmd = ""
                        hidden = False
                        for line in content.splitlines():
                            if line.startswith("Name="):
                                name = line.split("=", 1)[1].strip()
                            elif line.startswith("Exec="):
                                exec_cmd = line.split("=", 1)[1].strip()
                            elif line.startswith("Hidden="):
                                hidden = line.split("=", 1)[1].strip().lower() == "true"
                        apps.append(StartupApp(
                            name=name, command=exec_cmd, enabled=not hidden, source="autostart",
                        ))
                    except (OSError, PermissionError):
                        continue
        return apps

    def _list_macos(self) -> list[StartupApp]:
        apps = []
        dirs = [
            Path("/Library/LaunchDaemons"),
            Path("/Library/LaunchAgents"),
            Path.home() / "Library" / "LaunchAgents",
        ]
        for d in dirs:
            if not d.exists():
                continue
            for f in d.iterdir():
                if f.suffix == ".plist":
                    apps.append(StartupApp(
                        name=f.stem, command=str(f), enabled=True, source="launchd",
                    ))
        return apps

    def _list_windows(self) -> list[StartupApp]:
        apps = []
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run")
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    apps.append(StartupApp(name=name, command=value, enabled=True, source="registry"))
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except ImportError:
            pass

        startup_dir = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if startup_dir.exists():
            for f in startup_dir.iterdir():
                if f.is_file():
                    apps.append(StartupApp(name=f.stem, command=str(f), enabled=True, source="autostart"))
        return apps

    @staticmethod
    def toggle_autostart(app: StartupApp, enable: bool) -> bool:
        if app.source != "autostart":
            return False
        autostart = Path.home() / ".config" / "autostart"
        if sys.platform != "linux":
            return False
        src = autostart / f"{app.name}.desktop"
        if not src.exists():
            return False
        try:
            content = src.read_text(encoding="utf-8")
            if enable:
                content = content.replace("Hidden=true", "Hidden=false")
                if "Hidden=" not in content:
                    content += "\nHidden=false\n"
            else:
                content = content.replace("Hidden=false", "Hidden=true")
                if "Hidden=" not in content:
                    content += "\nHidden=true\n"
            src.write_text(content, encoding="utf-8")
            return True
        except OSError:
            return False
