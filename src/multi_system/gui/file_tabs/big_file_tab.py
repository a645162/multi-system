"""
Tab: 大文件查找
"""

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.files.big_files import find_big_files


def _fmt_size(b: int | float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


class BigFileTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Path + threshold ---
        top = QHBoxLayout()
        top.addWidget(QLabel("扫描路径:"))
        self._path_edit = QLineEdit("/")
        self._path_edit.setPlaceholderText("输入扫描根路径...")
        top.addWidget(self._path_edit)
        top.addWidget(QLabel("最小(MB):"))
        self._min_size_spin = QSpinBox()
        self._min_size_spin.setRange(1, 1000000)
        self._min_size_spin.setValue(100)
        top.addWidget(self._min_size_spin)
        self._scan_btn = QPushButton("扫描")
        self._scan_btn.clicked.connect(self._scan)
        top.addWidget(self._scan_btn)
        layout.addLayout(top)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._scan)
        layout.addWidget(toolbar)

        # --- Result table ---
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["文件路径", "大小"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._table)

        # --- Status ---
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._scan()

    def _scan(self):
        path_str = self._path_edit.text().strip()
        if not path_str:
            return
        path = Path(path_str)
        if not path.exists():
            QMessageBox.warning(self, "错误", f"路径不存在: {path_str}")
            return

        min_size = self._min_size_spin.value()
        self._scan_btn.setEnabled(False)
        self._status_label.setText("扫描中...")

        try:
            files = find_big_files(path, min_size_mb=min_size)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"扫描失败: {e}")
            self._scan_btn.setEnabled(True)
            self._status_label.setText("")
            return

        self._table.setRowCount(0)
        for f in files:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(f.path))
            self._table.setItem(row, 1, QTableWidgetItem(_fmt_size(f.size)))

        self._status_label.setText(f"找到 {len(files)} 个大文件 (>= {min_size}MB)")
        self._scan_btn.setEnabled(True)

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)
        menu = QMenu(self)
        menu.addAction("在文件管理器中显示", self._open_in_file_manager)
        menu.addAction("复制路径", self._copy_path)
        menu.addSeparator()
        menu.addAction("删除文件", self._delete_file)
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _open_in_file_manager(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 0)
        if not item:
            return
        path = item.text()
        parent = os.path.dirname(path)
        if sys.platform == "linux":
            subprocess.Popen(["xdg-open", parent])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", parent])
        elif sys.platform == "win32":
            subprocess.Popen(["explorer", parent])

    def _copy_path(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 0)
        if item:
            QApplication.clipboard().setText(item.text())

    def _delete_file(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 0)
        if not item:
            return
        path = item.text()
        reply = QMessageBox.warning(
            self, "确认删除",
            f"确定要删除此文件吗？\n\n{path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            os.remove(path)
            self._scan()
