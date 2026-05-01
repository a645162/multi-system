"""
Shell 启动速度分析
"""

import subprocess
import tempfile
from dataclasses import dataclass


@dataclass
class StartupResult:
    shell: str
    real_time: float
    user_time: float
    sys_time: float


class StartupAnalyzer:
    def __init__(self, shell: str):
        self.shell = shell

    def measure(self) -> StartupResult:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".time", delete=False) as f:
            outfile = f.name

        try:
            subprocess.run(
                ["/usr/bin/time", "-f", "%e %U %S", self.shell, "-i", "-c", "exit"],
                capture_output=True,
                timeout=30,
            )
            subprocess.run(
                ["/usr/bin/time", "-o", outfile, "-f", "%e %U %S",
                 self.shell, "-i", "-c", "exit"],
                capture_output=True, timeout=30,
            )
            with open(outfile) as f:
                parts = f.read().strip().split()
            return StartupResult(
                shell=self.shell,
                real_time=float(parts[0]),
                user_time=float(parts[1]),
                sys_time=float(parts[2]),
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError):
            return self._measure_fallback()

    def _measure_fallback(self) -> StartupResult:
        try:
            import time
            start = time.monotonic()
            subprocess.run(
                [self.shell, "-i", "-c", "exit"],
                capture_output=True, timeout=30,
            )
            elapsed = time.monotonic() - start
            return StartupResult(self.shell, elapsed, 0.0, 0.0)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return StartupResult(self.shell, -1.0, 0.0, 0.0)

    def measure_multiple(self, count: int = 5) -> list[StartupResult]:
        return [self.measure() for _ in range(count)]

    def measure_zsh_with_profiling(self) -> tuple[StartupResult, list[str]]:
        if self.shell != "zsh":
            return self.measure(), []

        from multi_system.system.shells.shell_base import RCFileManager
        rc = RCFileManager("zsh")
        content = rc.read_rc()

        if "zprof" not in content:
            rc.write_rc("zprof\n" + content)

        result = self.measure()

        try:
            prof_output = subprocess.run(
                ["zsh", "-i", "-c", "zprof"],
                capture_output=True, text=True, timeout=30,
            )
            prof_lines = prof_output.stdout.splitlines()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            prof_lines = []

        if "zprof" not in content:
            rc.write_rc(content)

        return result, prof_lines
