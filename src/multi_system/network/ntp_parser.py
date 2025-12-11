#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTP服务器HTML获取和解析器
独立处理从网页获取和解析NTP服务器信息的逻辑
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class NTPServerInfo:
    """NTP服务器信息数据类"""

    name: str
    category: str
    region: str  # 国内或海外
    ip_address: str = ""


class NTPWebParser:
    """NTP服务器网页获取和解析器"""

    def __init__(self):
        self.url = "https://dns.icoa.cn/ntp/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_html(self) -> str:
        """获取网页HTML内容"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        except requests.RequestException as e:
            raise Exception(f"获取网页失败: {e}")

    def parse_html(self, html_content: str) -> List[NTPServerInfo]:
        """解析HTML内容，提取NTP服务器信息"""
        soup = BeautifulSoup(html_content, "html.parser")
        servers = []

        # 查找国内NTP服务器部分
        china_section = soup.find("a", {"name": "china"})
        if china_section:
            servers.extend(self._parse_section(china_section, "国内"))

        # 查找海外NTP服务器部分
        global_section = soup.find("a", {"name": "global"})
        if global_section:
            servers.extend(self._parse_section(global_section, "海外"))

        return servers

    def _parse_section(self, section_start, region: str) -> List[NTPServerInfo]:
        """解析特定区域的NTP服务器"""
        servers = []
        current_category = ""

        # 从section_start开始遍历后续元素
        current = section_start.find_next_sibling()

        while current and not (
            current.name == "a" and current.get("name") in ["global", "china"]
        ):
            if current.name == "div" and "box_shadow" in current.get("class", []):
                # 提取分类名称
                bold_tag = current.find("b")
                if bold_tag:
                    category_text = bold_tag.get_text(strip=True)
                    # 提取中英文分类名称
                    if "<br>" in str(bold_tag):
                        parts = (
                            str(bold_tag)
                            .replace("<b>", "")
                            .replace("</b>", "")
                            .split("<br/>")
                        )
                        category_text = parts[0] if parts else category_text
                    current_category = category_text

                # 提取NTP服务器地址
                input_tags = current.find_all("input", {"class": "ips"})
                for input_tag in input_tags:
                    value = input_tag.get("value", "").strip()
                    if value and self._is_valid_server_address(value):
                        server = NTPServerInfo(
                            name=value, category=current_category, region=region
                        )
                        servers.append(server)

            current = current.find_next_sibling()

        return servers

    def _is_valid_server_address(self, address: str) -> bool:
        """验证是否为有效的服务器地址"""
        if not address:
            return False

        # 排除空值和占位符
        if address in ["", " ", "None"]:
            return False

        # 检查是否为域名或IP地址格式
        if "." in address or ":" in address:
            return True

        return False

    def get_ntp_servers(self) -> List[NTPServerInfo]:
        """获取并解析NTP服务器信息"""
        html_content = self.fetch_html()
        return self.parse_html(html_content)
