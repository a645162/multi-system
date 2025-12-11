#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTP服务器测试器
专门用于测试NTP服务器的可用性和响应时间
"""

import socket
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class NTPServerInfo:
    """NTP服务器信息数据类"""

    name: str
    category: str
    region: str  # 国内或海外
    ip_address: str = ""
    response_time: Optional[float] = None
    is_available: bool = False


class NTPServerTester:
    """NTP服务器测速器"""

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    def test_server_speed(self, server: NTPServerInfo) -> NTPServerInfo:
        """测试单个NTP服务器的响应速度"""
        try:
            start_time = time.time()

            # 尝试建立TCP连接到NTP端口（123）
            # 注意：真正的NTP使用UDP，这里用TCP连接测试可达性
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            # 先尝试域名解析
            try:
                # 获取IP地址
                addr_info = socket.getaddrinfo(
                    server.name, 123, socket.AF_UNSPEC, socket.SOCK_STREAM
                )
                if addr_info:
                    server.ip_address = addr_info[0][4][0]
            except socket.gaierror:
                server.is_available = False
                server.response_time = None
                return server

            # 尝试连接（虽然NTP实际用UDP，但这里用TCP测试连通性）
            try:
                result = sock.connect_ex((server.ip_address, 123))
                if result == 0:
                    server.is_available = True
                else:
                    server.is_available = False
            except:
                server.is_available = False
            finally:
                sock.close()

            end_time = time.time()
            server.response_time = (end_time - start_time) * 1000  # 转换为毫秒

        except Exception as e:
            server.is_available = False
            server.response_time = None

        return server

    def test_multiple_servers(
        self, servers: List[NTPServerInfo], max_workers: int = 10
    ) -> List[NTPServerInfo]:
        """并发测试多个NTP服务器"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_server = {
                executor.submit(self.test_server_speed, server): server
                for server in servers
            }

            # 收集结果
            for future in as_completed(future_to_server):
                try:
                    server = future.result()
                    yield server
                except Exception as e:
                    server = future_to_server[future]
                    server.is_available = False
                    server.response_time = None
                    yield server
