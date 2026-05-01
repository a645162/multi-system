"""
系统代理管理
"""
import contextlib
import os
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class ProxyConfig:
    http: str = ""
    https: str = ""
    no_proxy: str = "localhost,127.0.0.1"

class ProxyManager:
    @staticmethod
    def get_proxy() -> ProxyConfig:
        return ProxyConfig(
            http=os.environ.get("http_proxy", ""),
            https=os.environ.get("https_proxy", ""),
            no_proxy=os.environ.get("no_proxy", "localhost,127.0.0.1"),
        )

    @staticmethod
    def set_proxy(config: ProxyConfig) -> None:
        os.environ["http_proxy"] = config.http
        os.environ["https_proxy"] = config.https
        os.environ["no_proxy"] = config.no_proxy
        if sys.platform == "linux":
            with contextlib.suppress(Exception):
                subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "manual"], capture_output=True)
                if config.http:
                    host, _, port = config.http.replace("http://", "").rpartition(":")
                    subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "host", host], capture_output=True)
                    subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "port", port or "0"], capture_output=True)

    @staticmethod
    def clear_proxy() -> None:
        for var in ("http_proxy", "https_proxy", "no_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY"):
            os.environ.pop(var, None)
        if sys.platform == "linux":
            with contextlib.suppress(Exception):
                subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "none"], capture_output=True)
