"""SSH 密钥管理"""
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SSHKey:
    name: str
    path: Path
    key_type: str
    is_public: bool
    size_bytes: int


class SSHKeyManager:
    def __init__(self):
        self.ssh_dir = Path.home() / ".ssh"

    def list_keys(self) -> list[SSHKey]:
        if not self.ssh_dir.exists():
            return []
        keys = []
        for f in self.ssh_dir.iterdir():
            if (
                f.is_file()
                and not f.name.startswith(".")
                and f.name != "config"
                and not f.name.endswith(".pub")
            ):
                ktype = "unknown"
                try:
                    first = (
                        f.read_text(encoding="utf-8", errors="replace").split()[0]
                        if f.stat().st_size < 10000
                        else ""
                    )
                    ktype = first
                except (OSError, IndexError):
                    pass
                keys.append(SSHKey(f.name, f, ktype, False, f.stat().st_size))
            elif f.suffix == ".pub":
                keys.append(SSHKey(f.name, f, "public", True, f.stat().st_size))
        return keys

    def generate_key(
        self, name: str, key_type: str = "ed25519", passphrase: str = ""
    ) -> bool:
        cmd = [
            "ssh-keygen",
            "-t",
            key_type,
            "-f",
            str(self.ssh_dir / name),
            "-N",
            passphrase,
        ]
        try:
            self.ssh_dir.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def get_public_key(self, name: str) -> str:
        pub = self.ssh_dir / f"{name}.pub"
        if pub.exists():
            return pub.read_text(encoding="utf-8").strip()
        return ""
