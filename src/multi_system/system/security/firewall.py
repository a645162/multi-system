"""防火墙管理"""
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class FirewallRule:
    name: str
    action: str
    port: str
    protocol: str
    direction: str


class FirewallManager:
    @staticmethod
    def get_status() -> str:
        if sys.platform == "linux":
            try:
                r = subprocess.run(["ufw", "status"], capture_output=True, text=True)
                return r.stdout.strip()
            except FileNotFoundError:
                try:
                    r = subprocess.run(
                        ["firewall-cmd", "--state"], capture_output=True, text=True
                    )
                    return r.stdout.strip()
                except FileNotFoundError:
                    return "未检测到防火墙"
        elif sys.platform == "darwin":
            r = subprocess.run(
                ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
                capture_output=True,
                text=True,
            )
            return r.stdout.strip()
        elif sys.platform == "win32":
            r = subprocess.run(
                ["netsh", "advfirewall", "show", "currentprofile", "state"],
                capture_output=True,
                text=True,
            )
            return r.stdout.strip()
        return "不支持"

    @staticmethod
    def list_rules() -> list[FirewallRule]:
        if sys.platform == "linux":
            try:
                r = subprocess.run(
                    ["ufw", "status", "numbered"], capture_output=True, text=True
                )
                rules = []
                for line in r.stdout.splitlines():
                    if line.startswith("[") and "ALLOW" in line or "DENY" in line:
                        parts = line.split()
                        action = "ALLOW" if "ALLOW" in line else "DENY"
                        port = parts[-2] if len(parts) >= 2 else ""
                        proto = parts[-1] if len(parts) >= 1 else ""
                        rules.append(FirewallRule(line.strip(), action, port, proto, ""))
                return rules
            except FileNotFoundError:
                return []
        return []

    @staticmethod
    def add_rule(port: int, action: str = "allow", protocol: str = "tcp") -> bool:
        if sys.platform == "linux":
            try:
                cmd = ["sudo", "ufw", action, f"{port}/{protocol}"]
                r = subprocess.run(cmd, capture_output=True, text=True)
                return r.returncode == 0
            except FileNotFoundError:
                return False
        return False

    @staticmethod
    def toggle(enabled: bool) -> bool:
        if sys.platform == "linux":
            try:
                cmd = ["sudo", "ufw", "enable" if enabled else "disable"]
                r = subprocess.run(cmd, capture_output=True, text=True, input="y\n")
                return r.returncode == 0
            except FileNotFoundError:
                return False
        return False
