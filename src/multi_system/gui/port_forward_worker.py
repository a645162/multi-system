"""
端口转发工作线程
在独立线程中运行asyncio事件循环，通过Qt信号与主线程通信
"""

import asyncio

from PySide6.QtCore import QMutex, QThread, Signal

from multi_system.network.port_forward import (
    PortForwardEngine,
    PortForwardRule,
)


class PortForwardWorker(QThread):
    rule_status_changed = Signal(str, str, str)
    rule_connection_count_changed = Signal(str, int)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._engine: PortForwardEngine | None = None
        self._mutex = QMutex()

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._engine = PortForwardEngine(
            on_rule_status_changed=self._on_engine_status_changed,
        )

        self._loop.run_forever()

        self._loop.run_until_complete(self._engine.stop_all())
        self._loop.close()

    def stop(self):
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

    def add_rule(self, rule: PortForwardRule) -> PortForwardRule | None:
        self._mutex.lock()
        try:
            return self._engine.add_rule(rule) if self._engine else None
        finally:
            self._mutex.unlock()

    def remove_rule(self, rule_id: str) -> bool:
        self._mutex.lock()
        try:
            return self._engine.remove_rule(rule_id) if self._engine else False
        finally:
            self._mutex.unlock()

    def get_all_rules(self) -> list[PortForwardRule]:
        self._mutex.lock()
        try:
            return self._engine.get_all_rules() if self._engine else []
        finally:
            self._mutex.unlock()

    def update_rule(self, rule_id: str, **kwargs) -> PortForwardRule | None:
        self._mutex.lock()
        try:
            return self._engine.update_rule(rule_id, **kwargs) if self._engine else None
        finally:
            self._mutex.unlock()

    def start_rule(self, rule_id: str):
        if self._loop and self._engine:
            asyncio.run_coroutine_threadsafe(
                self._engine.start_rule(rule_id), self._loop
            )

    def stop_rule(self, rule_id: str):
        if self._loop and self._engine:
            asyncio.run_coroutine_threadsafe(
                self._engine.stop_rule(rule_id), self._loop
            )

    def stop_all_rules(self):
        if self._loop and self._engine:
            asyncio.run_coroutine_threadsafe(
                self._engine.stop_all(), self._loop
            )

    def _on_engine_status_changed(self, rule: PortForwardRule):
        self.rule_status_changed.emit(rule.id, rule.status.value, rule.error_message)
        self.rule_connection_count_changed.emit(rule.id, rule.active_connections)
