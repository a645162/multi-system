"""
Tab: 磁盘分析
"""

import os
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

from multi_system.system.monitor.disk_usage import DiskUsageAnalyzer


def _fmt_size(b: int | float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


class DiskTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("扫描路径:"))
        self._path_edit = QLineEdit("/")
        top.addWidget(self._path_edit)
        btn = QPushButton("扫描")
        btn.clicked.connect(self._scan)
        top.addWidget(btn)
        layout.addLayout(top)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._scan)
        layout.addWidget(toolbar)

        layout.addWidget(QLabel("目录大小排序:"))
        self._dir_table = QTableWidget(0, 3)
        self._dir_table.setHorizontalHeaderLabels(["目录", "大小", "文件数"])
        self._dir_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._dir_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._dir_table.setAlternatingRowColors(True)
        self._dir_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._dir_table.customContextMenuRequested.connect(self._show_dir_context_menu)
        self._dir_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._dir_table)

        layout.addWidget(QLabel("大文件 (>100MB):"))
        self._file_table = QTableWidget(0, 2)
        self._file_table.setHorizontalHeaderLabels(["文件", "大小"])
        self._file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._file_table.setAlternatingRowColors(True)
        self._file_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._file_table.customContextMenuRequested.connect(self._show_file_context_menu)
        self._file_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._file_table)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._scan()

    def _scan(self):
        from pathlib import Path
        path = Path(self._path_edit.text().strip())

        dirs = DiskUsageAnalyzer.scan_directory(path)
        self._dir_table.setRowCount(0)
        for d in dirs:
            row = self._dir_table.rowCount()
            self._dir_table.insertRow(row)
            self._dir_table.setItem(row, 0, QTableWidgetItem(d.path))
            self._dir_table.setItem(row, 1, QTableWidgetItem(_fmt_size(d.size)))
            self._dir_table.setItem(row, 2, QTableWidgetItem(str(d.file_count)))

        files = DiskUsageAnalyzer.find_big_files(path)
        self._file_table.setRowCount(0)
        for f in files:
            row = self._file_table.rowCount()
            self._file_table.insertRow(row)
            self._file_table.setItem(row, 0, QTableWidgetItem(f.path))
            self._file_table.setItem(row, 1, QTableWidgetItem(_fmt_size(f.size)))

    @staticmethod
    def _open_path_in_file_manager(path: str):
        if sys.platform == "linux":
            subprocess.Popen(["xdg-open", path])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        elif sys.platform == "win32":
            subprocess.Popen(["explorer", path])

    def _show_dir_context_menu(self, pos):
        row = self._dir_table.rowAt(pos.y())
        if row < 0:
            return
        self._dir_table.selectRow(row)
        menu = QMenu(self)
        path_item = self._dir_table.item(row, 0)
        path = path_item.text() if path_item else ""
        menu.addAction("在文件管理器中打开", lambda: self._open_path_in_file_manager(path))
        menu.addAction("复制路径", lambda: QApplication.clipboard().setText(path))
        menu.exec(self._dir_table.viewport().mapToGlobal(pos))

    def _show_file_context_menu(self, pos):
        row = self._file_table.rowAt(pos.y())
        if row < 0:
            return
        self._file_table.selectRow(row)
        menu = QMenu(self)
        path_item = self._file_table.item(row, 0)
        path = path_item.text() if path_item else ""
        parent_dir = os.path.dirname(path)
        menu.addAction("在文件管理器中显示", lambda: self._open_path_in_file_manager(parent_dir))
        menu.addAction("复制路径", lambda: QApplication.clipboard().setText(path))
        menu.addSeparator()
        menu.addAction("删除文件", lambda: self._delete_file(path))
        menu.exec(self._file_table.viewport().mapToGlobal(pos))

    def _delete_file(self, path: str):
        if not path:
            return
        reply = QMessageBox.warning(
            self, "确认删除",
            f"确定要删除文件吗？\n{path}\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(path)
                self._scan()
            except OSError as e:
                QMessageBox.warning(self, "删除失败", f"无法删除文件: {e}")
