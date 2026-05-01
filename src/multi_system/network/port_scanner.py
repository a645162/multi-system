"""
TCP 端口扫描
"""
import asyncio
from dataclasses import dataclass


@dataclass
class PortResult:
    port: int
    is_open: bool
    service: str = ""

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 993: "IMAPS",
    995: "POP3S", 3306: "MySQL", 5432: "PostgreSQL", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB",
}

class PortScanner:
    @staticmethod
    async def scan_port(host: str, port: int, timeout: float = 1.0) -> PortResult:
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return PortResult(port=port, is_open=True, service=COMMON_PORTS.get(port, ""))
        except (OSError, asyncio.TimeoutError):
            return PortResult(port=port, is_open=False, service=COMMON_PORTS.get(port, ""))

    @staticmethod
    def scan(host: str, ports: range | list[int] | None = None, timeout: float = 1.0) -> list[PortResult]:
        if ports is None:
            ports = list(COMMON_PORTS.keys())
        async def _scan():
            tasks = [PortScanner.scan_port(host, p, timeout) for p in ports]
            return await asyncio.gather(*tasks)
        return asyncio.run(_scan())
