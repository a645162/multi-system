"""
Tab: 应用启动器
"""

import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.program.packages.app_launcher import AppLauncher


class AppLauncherTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._all_apps = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Search ---
        top = QHBoxLayout()
        top.addWidget(QLabel("搜索:"))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("应用名...")
        self._search_edit.textChanged.connect(self._on_search)
        top.addWidget(self._search_edit)
        self._launch_btn = QPushButton("启动")
        self._launch_btn.clicked.connect(self._launch_selected)
        top.addWidget(self._launch_btn)
        layout.addLayout(top)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        layout.addWidget(toolbar)

        # --- Table ---
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["应用名", "命令"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

        # --- Status ---
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._refresh()

    def _force_refresh(self):
        self._refresh()

    def _refresh(self):
        self._all_apps = AppLauncher.list_apps()
        self._show_apps(self._all_apps)
        self._status_label.setText(f"共 {len(self._all_apps)} 个应用")

    def _on_search(self, keyword: str):
        if not keyword:
            self._show_apps(self._all_apps)
            return
        kw = keyword.lower()
        filtered = [a for a in self._all_apps if kw in a.name.lower() or kw in a.command.lower()]
        self._show_apps(filtered)
        self._status_label.setText(f"匹配 {len(filtered)}/{len(self._all_apps)} 个应用")

    def _show_apps(self, apps):
        self._table.setRowCount(0)
        for a in apps:
            row = self._table.rowCount()
            self._table.insertRow(row)
            name_item = QTableWidgetItem(a.name)
            name_item.setData(Qt.ItemDataRole.UserRole, a.command)
            self._table.setItem(row, 0, name_item)
            self._table.setItem(row, 1, QTableWidgetItem(a.command))

    def _launch_selected(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "提示", "请先选择一个应用")
            return
        item = self._table.item(rows[0].row(), 0)
        command = item.data(Qt.ItemDataRole.UserRole) if item else ""
        if not command:
            return
        if AppLauncher.launch(command):
            self._status_label.setText(f"已启动: {item.text()}")
        else:
            QMessageBox.warning(self, "失败", f"无法启动: {item.text()}")

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)
        menu = QMenu(self)
        menu.addAction("启动", self._launch_selected)
        cmd_item = self._table.item(row, 1)
        menu.addAction("复制命令", lambda: QApplication.clipboard().setText(cmd_item.text() if cmd_item else ""))
        menu.addSeparator()
        menu.addAction("在文件管理器中显示", self._open_in_file_manager)
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _open_in_file_manager(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        name_item = self._table.item(rows[0].row(), 0)
        cmd = name_item.data(Qt.ItemDataRole.UserRole) if name_item else ""
        # Try to find .desktop file path or open app directory
        from pathlib import Path
        autostart_dirs = [
            Path("/usr/share/applications"),
            Path.home() / ".local" / "share" / "applications",
        ]
        for d in autostart_dirs:
            if d.exists():
                for f in d.glob("*.desktop"):
                    try:
                        content = f.read_text(encoding="utf-8", errors="replace")
                        for line in content.splitlines():
                            if line.startswith("Exec=") and line.split("=", 1)[1].strip() == cmd:
                                path = str(d)
                                if sys.platform == "linux":
                                    subprocess.Popen(["xdg-open", path])
                                elif sys.platform == "darwin":
                                    subprocess.Popen(["open", path])
                                elif sys.platform == "win32":
                                    subprocess.Popen(["explorer", path])
                                return
                    except OSError:
                        continue
        # Fallback: just open the autostart dir
        for d in autostart_dirs:
            if d.exists():
                if sys.platform == "linux":
                    subprocess.Popen(["xdg-open", str(d)])
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", str(d)])
                elif sys.platform == "win32":
                    subprocess.Popen(["explorer", str(d)])
                return
