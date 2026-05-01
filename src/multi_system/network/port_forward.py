"""
端口转发引擎
纯asyncio实现，无Qt依赖，跨平台兼容
"""

import asyncio
import contextlib
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum


class RuleStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class PortForwardRule:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    local_host: str = "127.0.0.1"
    local_port: int = 0
    remote_host: str = ""
    remote_port: int = 0
    status: RuleStatus = RuleStatus.STOPPED
    error_message: str = ""
    active_connections: int = 0


class PortForwardEngine:
    CONNECT_TIMEOUT = 10

    def __init__(
        self,
        on_rule_status_changed: Callable[[PortForwardRule], None] | None = None,
    ):
        self._rules: dict[str, PortForwardRule] = {}
        self._servers: dict[str, asyncio.AbstractServer] = {}
        self._connection_tasks: dict[str, set[asyncio.Task]] = {}
        self._on_rule_status_changed = on_rule_status_changed

    def add_rule(self, rule: PortForwardRule) -> PortForwardRule:
        self._rules[rule.id] = rule
        return rule

    def remove_rule(self, rule_id: str) -> bool:
        rule = self._rules.get(rule_id)
        if rule is None:
            return False
        if rule.status == RuleStatus.RUNNING:
            return False
        self._rules.pop(rule_id, None)
        return True

    def get_rule(self, rule_id: str) -> PortForwardRule | None:
        return self._rules.get(rule_id)

    def get_all_rules(self) -> list[PortForwardRule]:
        return list(self._rules.values())

    def update_rule(self, rule_id: str, **kwargs) -> PortForwardRule | None:
        rule = self._rules.get(rule_id)
        if rule is None:
            return None
        if rule.status != RuleStatus.STOPPED:
            return None
        for key, value in kwargs.items():
            if hasattr(rule, key) and key not in ("id", "status"):
                setattr(rule, key, value)
        return rule

    async def start_rule(self, rule_id: str) -> bool:
        rule = self._rules.get(rule_id)
        if rule is None or rule.status in (RuleStatus.RUNNING, RuleStatus.STARTING):
            return False

        rule.status = RuleStatus.STARTING
        rule.error_message = ""
        self._notify(rule)

        try:
            server = await asyncio.start_server(
                lambda r, w: self._handle_client(rule_id, r, w),
                rule.local_host,
                rule.local_port,
            )
            self._servers[rule_id] = server
            self._connection_tasks[rule_id] = set()
            rule.status = RuleStatus.RUNNING
            self._notify(rule)
            return True
        except OSError as e:
            rule.status = RuleStatus.ERROR
            rule.error_message = str(e)
            self._notify(rule)
            return False

    async def stop_rule(self, rule_id: str) -> bool:
        rule = self._rules.get(rule_id)
        if rule is None or rule.status != RuleStatus.RUNNING:
            return False

        server = self._servers.pop(rule_id, None)
        if server:
            server.close()
            await server.wait_closed()

        tasks = self._connection_tasks.pop(rule_id, set())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        rule.status = RuleStatus.STOPPED
        rule.active_connections = 0
        rule.error_message = ""
        self._notify(rule)
        return True

    async def stop_all(self) -> None:
        rule_ids = [rid for rid, r in self._rules.items() if r.status == RuleStatus.RUNNING]
        for rule_id in rule_ids:
            await self.stop_rule(rule_id)

    async def _handle_client(
        self,
        rule_id: str,
        local_reader: asyncio.StreamReader,
        local_writer: asyncio.StreamWriter,
    ):
        rule = self._rules.get(rule_id)
        if rule is None:
            local_writer.close()
            return

        task = asyncio.current_task()
        if task:
            self._connection_tasks[rule_id].add(task)

        rule.active_connections += 1
        self._notify(rule)

        try:
            remote_reader, remote_writer = await asyncio.wait_for(
                asyncio.open_connection(rule.remote_host, rule.remote_port),
                timeout=self.CONNECT_TIMEOUT,
            )
        except (OSError, TimeoutError, asyncio.TimeoutError):
            rule.active_connections -= 1
            if task:
                self._connection_tasks[rule_id].discard(task)
            local_writer.close()
            self._notify(rule)
            return

        try:
            await asyncio.gather(
                self._relay(local_reader, remote_writer),
                self._relay(remote_reader, local_writer),
                return_exceptions=True,
            )
        finally:
            rule.active_connections -= 1
            if task:
                self._connection_tasks[rule_id].discard(task)
            for writer in (local_writer, remote_writer):
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass
            self._notify(rule)

    @staticmethod
    async def _relay(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        try:
            while True:
                data = await reader.read(65536)
                if not data:
                    break
                writer.write(data)
                await writer.drain()
        except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError, OSError):
            pass
        finally:
            with contextlib.suppress(Exception):
                writer.write_eof()

    def _notify(self, rule: PortForwardRule):
        if self._on_rule_status_changed:
            self._on_rule_status_changed(rule)
