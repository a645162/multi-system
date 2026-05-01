"""定时任务管理 (crontab / launchd / Task Scheduler)"""
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class CronJob:
    schedule: str
    command: str
    comment: str = ""
    line_number: int = 0


class CronManager:
    @staticmethod
    def list_jobs() -> list[CronJob]:
        if sys.platform == "win32":
            try:
                result = subprocess.run(
                    ["schtasks", "/query", "/fo", "CSV", "/nh"],
                    capture_output=True,
                    text=True,
                )
                jobs = []
                for line in result.stdout.splitlines()[1:]:
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        jobs.append(CronJob(schedule=parts[0], command=parts[1]))
                return jobs
            except Exception:
                return []
        else:
            try:
                result = subprocess.run(
                    ["crontab", "-l"], capture_output=True, text=True
                )
                if result.returncode != 0:
                    return []
                jobs = []
                for i, line in enumerate(result.stdout.splitlines(), 1):
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    parts = stripped.split(None, 5)
                    if len(parts) >= 6:
                        jobs.append(
                            CronJob(
                                schedule=" ".join(parts[:5]),
                                command=parts[5],
                                line_number=i,
                            )
                        )
                return jobs
            except FileNotFoundError:
                return []

    @staticmethod
    def add_job(schedule: str, command: str) -> bool:
        if sys.platform == "win32":
            return False
        try:
            result = subprocess.run(
                ["crontab", "-l"], capture_output=True, text=True
            )
            content = result.stdout if result.returncode == 0 else ""
            content += f"\n{schedule} {command}\n"
            proc = subprocess.run(
                ["crontab", "-"], input=content, text=True, capture_output=True
            )
            return proc.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def remove_job(line_number: int) -> bool:
        if sys.platform == "win32":
            return False
        try:
            result = subprocess.run(
                ["crontab", "-l"], capture_output=True, text=True
            )
            if result.returncode != 0:
                return False
            lines = result.stdout.splitlines(keepends=True)
            if 1 <= line_number <= len(lines):
                del lines[line_number - 1]
            proc = subprocess.run(
                ["crontab", "-"],
                input="".join(lines),
                text=True,
                capture_output=True,
            )
            return proc.returncode == 0
        except FileNotFoundError:
            return False
