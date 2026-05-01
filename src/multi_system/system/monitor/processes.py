"""
进程管理器
"""

from dataclasses import dataclass

import psutil


@dataclass
class ProcessInfo:
    pid: int
    name: str
    username: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    cmdline: str
    create_time: float


class ProcessManager:
    @staticmethod
    def list_processes(sort_by: str = "cpu") -> list[ProcessInfo]:
        procs = []
        for p in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_percent", "status", "cmdline", "create_time", "memory_info"]):
            try:
                info = p.info
                mem = info.get("memory_info")
                procs.append(ProcessInfo(
                    pid=info["pid"],
                    name=info["name"] or "",
                    username=info["username"] or "",
                    cpu_percent=info["cpu_percent"] or 0.0,
                    memory_percent=info["memory_percent"] or 0.0,
                    memory_mb=mem.rss / 1024 / 1024 if mem else 0.0,
                    status=info["status"] or "",
                    cmdline=" ".join(info["cmdline"] or [])[:200],
                    create_time=info["create_time"] or 0.0,
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        key_map = {"cpu": "cpu_percent", "mem": "memory_percent", "pid": "pid", "name": "name"}
        procs.sort(key=lambda p: getattr(p, key_map.get(sort_by, "cpu_percent")), reverse=sort_by != "name")
        return procs

    @staticmethod
    def kill(pid: int, force: bool = False) -> bool:
        try:
            p = psutil.Process(pid)
            p.kill() if force else p.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    @staticmethod
    def search(keyword: str) -> list[ProcessInfo]:
        keyword = keyword.lower()
        return [
            p for p in ProcessManager.list_processes()
            if keyword in p.name.lower() or keyword in p.cmdline.lower() or keyword in str(p.pid)
        ]
