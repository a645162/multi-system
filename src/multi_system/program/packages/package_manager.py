"""跨平台包管理器封装"""
import subprocess
from dataclasses import dataclass


@dataclass
class PackageInfo:
    name: str
    version: str
    manager: str


class PackageManager:
    @staticmethod
    def detect_managers() -> list[str]:
        available = []
        cmds = {
            "apt": ["apt", "--version"],
            "brew": ["brew", "--version"],
            "winget": ["winget", "--version"],
            "choco": ["choco", "--version"],
            "scoop": ["scoop", "--version"],
            "pip": ["pip", "--version"],
            "pacman": ["pacman", "--version"],
            "dnf": ["dnf", "--version"],
        }
        for name, cmd in cmds.items():
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    available.append(name)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return available

    @staticmethod
    def list_packages(manager: str) -> list[PackageInfo]:
        cmd_map = {
            "apt": ["apt", "list", "--installed"],
            "brew": ["brew", "list", "--versions"],
            "pip": ["pip", "list", "--format=columns"],
            "pacman": ["pacman", "-Q"],
        }
        cmd = cmd_map.get(manager)
        if not cmd:
            return []
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            pkgs = []
            for line in result.stdout.splitlines():
                if line.startswith(("Listing", "WARNING", "DEPRECATION")) or not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    pkgs.append(
                        PackageInfo(
                            parts[0],
                            parts[1].replace("(", "").replace(")", ""),
                            manager,
                        )
                    )
                elif parts:
                    pkgs.append(PackageInfo(parts[0], "", manager))
            return pkgs
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

    @staticmethod
    def install(manager: str, package: str) -> bool:
        cmd_map = {
            "apt": ["sudo", "apt", "install", "-y", package],
            "brew": ["brew", "install", package],
            "winget": ["winget", "install", package],
            "choco": ["choco", "install", "-y", package],
            "scoop": ["scoop", "install", package],
            "pip": ["pip", "install", package],
            "pacman": ["sudo", "pacman", "-S", "--noconfirm", package],
        }
        cmd = cmd_map.get(manager)
        if not cmd:
            return False
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @staticmethod
    def uninstall(manager: str, package: str) -> bool:
        cmd_map = {
            "apt": ["sudo", "apt", "remove", "-y", package],
            "brew": ["brew", "uninstall", package],
            "winget": ["winget", "uninstall", package],
            "choco": ["choco", "uninstall", "-y", package],
            "scoop": ["scoop", "uninstall", package],
            "pip": ["pip", "uninstall", "-y", package],
            "pacman": ["sudo", "pacman", "-R", "--noconfirm", package],
        }
        cmd = cmd_map.get(manager)
        if not cmd:
            return False
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @staticmethod
    def update(manager: str, package: str = "") -> bool:
        if package:
            cmd_map = {
                "apt": ["sudo", "apt", "upgrade", "-y", package],
                "brew": ["brew", "upgrade", package],
                "winget": ["winget", "upgrade", package],
                "choco": ["choco", "upgrade", "-y", package],
                "scoop": ["scoop", "update", package],
                "pip": ["pip", "install", "--upgrade", package],
                "pacman": ["sudo", "pacman", "-S", "--noconfirm", package],
            }
        else:
            cmd_map = {
                "apt": ["sudo", "apt", "upgrade", "-y"],
                "brew": ["brew", "upgrade"],
                "winget": ["winget", "upgrade", "--all"],
                "choco": ["choco", "upgrade", "-y", "--all"],
                "scoop": ["scoop", "update", "--all"],
                "pacman": ["sudo", "pacman", "-Syu", "--noconfirm"],
            }
        cmd = cmd_map.get(manager)
        if not cmd:
            return False
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @staticmethod
    def search_package(manager: str, keyword: str) -> list[PackageInfo]:
        cmd_map = {
            "apt": ["apt", "search", keyword],
            "brew": ["brew", "search", keyword],
            "pip": ["pip", "search", keyword],
        }
        cmd = cmd_map.get(manager)
        if not cmd:
            return []
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            pkgs = []
            for line in result.stdout.splitlines()[:50]:
                if "/" in line or "==" in line:
                    name = line.split("/")[0].split("=")[0].split()[0].strip()
                    if name:
                        pkgs.append(PackageInfo(name, "", manager))
            return pkgs
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
