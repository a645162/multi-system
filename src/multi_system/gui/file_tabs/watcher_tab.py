"""
Tab: 文件变更监控
"""

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.files.file_watcher import FileEvent, SimpleFileWatcher


class WatcherTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._watcher: SimpleFileWatcher | None = None
        self._timer: QTimer | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Directory input ---
        top = QHBoxLayout()
        top.addWidget(QLabel("监控目录:"))
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("输入要监控的目录路径...")
        top.addWidget(self._path_edit)
        layout.addLayout(top)

        # --- Start/Stop ---
        btn_row = QHBoxLayout()
        self._start_btn = QPushButton("开始监控")
        self._start_btn.clicked.connect(self._start)
        btn_row.addWidget(self._start_btn)
        self._stop_btn = QPushButton("停止监控")
        self._stop_btn.clicked.connect(self._stop)
        self._stop_btn.setEnabled(False)
        btn_row.addWidget(self._stop_btn)
        self._clear_btn = QPushButton("清空日志")
        self._clear_btn.clicked.connect(self._clear_log)
        btn_row.addWidget(self._clear_btn)
        layout.addLayout(btn_row)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        layout.addWidget(toolbar)

        # --- Event log ---
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self._log)

        # --- Status ---
        self._status_label = QLabel("未启动")
        layout.addWidget(self._status_label)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True

    def _force_refresh(self):
        # If watching, check once immediately
        if self._watcher and self._timer and self._timer.isActive():
            self._check_events()

    def _start(self):
        path_str = self._path_edit.text().strip()
        if not path_str:
            return
        path = Path(path_str)
        if not path.is_dir():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", f"目录不存在: {path_str}")
            return

        self._watcher = SimpleFileWatcher(path, callback=self._on_event)
        # Take initial snapshot
        self._watcher.check_once()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_events)
        self._timer.start(2000)

        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._status_label.setText(f"监控中: {path_str}")
        self._append_log(f"=== 开始监控: {path_str} ===")

    def _stop(self):
        if self._timer:
            self._timer.stop()
            self._timer = None
        self._watcher = None

        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._status_label.setText("已停止")
        self._append_log("=== 监控已停止 ===")

    def _check_events(self):
        if not self._watcher:
            return
        events = self._watcher.check_once()
        for evt in events:
            self._on_event(evt)

    def _on_event(self, evt: FileEvent):
        type_map = {
            "created": "新建",
            "modified": "修改",
            "deleted": "删除",
        }
        label = type_map.get(evt.event_type, evt.event_type)
        self._append_log(f"[{label}] {evt.path}")

    def _append_log(self, text: str):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._log.appendPlainText(f"{timestamp} {text}")

    def _clear_log(self):
        self._log.clear()
