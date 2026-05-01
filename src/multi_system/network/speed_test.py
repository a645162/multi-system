"""
网速测试
"""
import socket
import time
from dataclasses import dataclass


@dataclass
class SpeedResult:
    ping_ms: float
    download_mbps: float = 0.0
    error: str = ""

class SpeedTester:
    @staticmethod
    def ping(host: str = "8.8.8.8", port: int = 53, timeout: int = 5) -> float:
        start = time.monotonic()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            s.close()
            return (time.monotonic() - start) * 1000
        except (TimeoutError, OSError):
            return -1.0

    @staticmethod
    def download_test(url: str = "http://speedtest.tele2.net/1MB.zip", timeout: int = 30) -> SpeedResult:
        import urllib.request
        ping = SpeedTester.ping()
        start = time.monotonic()
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                data = resp.read()
            elapsed = time.monotonic() - start
            mbps = (len(data) * 8) / (elapsed * 1_000_000)
            return SpeedResult(ping_ms=ping, download_mbps=mbps)
        except Exception as e:
            return SpeedResult(ping_ms=ping, error=str(e))
