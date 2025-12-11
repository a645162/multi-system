#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTP服务器模块
整合NTP服务器获取、解析和测试功能
"""

from typing import List, Optional
from dataclasses import dataclass

from .ntp_parser import NTPWebParser
from .ntp_tester import NTPServerTester, NTPServerInfo


@dataclass
class NTPServer:
    """NTP服务器数据类"""

    name: str
    category: str
    region: str  # 国内或海外
    ip_address: str = ""
    response_time: Optional[float] = None
    is_available: bool = False


class NTPManager:
    """NTP服务器管理器"""

    def __init__(self):
        self.parser = NTPWebParser()
        self.tester = NTPServerTester()

    def get_ntp_servers(self) -> List[NTPServer]:
        """获取所有NTP服务器"""
        try:
            # 使用解析器获取服务器信息
            parser_servers = self.parser.get_ntp_servers()

            # 转换为标准NTPServer格式
            servers = []
            for server_info in parser_servers:
                server = NTPServer(
                    name=server_info.name,
                    category=server_info.category,
                    region=server_info.region,
                    ip_address=server_info.ip_address,
                )
                servers.append(server)

            return servers
        except Exception as e:
            print(f"获取NTP服务器失败: {e}")
            import traceback

            traceback.print_exc()
            return []

    def test_servers(
        self, servers: List[NTPServer], show_progress: bool = True
    ) -> List[NTPServer]:
        """测试服务器速度"""
        if not servers:
            return []

        # 转换为测试器格式
        tester_servers = []
        for server in servers:
            tester_server = NTPServerInfo(
                name=server.name,
                category=server.category,
                region=server.region,
                ip_address=server.ip_address,
                response_time=server.response_time,
                is_available=server.is_available,
            )
            tester_servers.append(tester_server)

        # 测试服务器
        tested_servers = []
        completed = 0

        for tested_server in self.tester.test_multiple_servers(tester_servers):
            # 转换回标准格式
            server = NTPServer(
                name=tested_server.name,
                category=tested_server.category,
                region=tested_server.region,
                ip_address=tested_server.ip_address,
                response_time=tested_server.response_time,
                is_available=tested_server.is_available,
            )
            tested_servers.append(server)
            completed += 1

            if show_progress:
                status = "✓" if server.is_available else "✗"
                if server.is_available:
                    print(
                        f"[{completed}/{len(servers)}] {status} {server.name} - {server.response_time:.1f}ms"
                    )
                else:
                    print(
                        f"[{completed}/{len(servers)}] {status} {server.name} - 不可用"
                    )

        return tested_servers

    def get_best_servers(
        self, servers: List[NTPServer], top_n: int = 5
    ) -> List[NTPServer]:
        """获取响应最快的NTP服务器"""
        available_servers = [s for s in servers if s.is_available]
        available_servers.sort(key=lambda x: x.response_time or float("inf"))
        return available_servers[:top_n]

    def print_servers_by_category(self, servers: List[NTPServer]):
        """按分类显示NTP服务器"""
        # 按地区和分类分组
        regions = {}
        for server in servers:
            if server.region not in regions:
                regions[server.region] = {}
            if server.category not in regions[server.region]:
                regions[server.region][server.category] = []
            regions[server.region][server.category].append(server)

        for region in ["国内", "海外"]:
            if region not in regions:
                continue

            print(f"\n=== {region}NTP服务器 ===")
            for category, servers_list in regions[region].items():
                print(f"\n【{category}】")
                for server in servers_list:
                    if server.is_available:
                        print(f"  ✓ {server.name:<30} {server.response_time:.1f}ms")
                    else:
                        print(f"  ✗ {server.name:<30} 不可用")
