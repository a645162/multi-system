"""
Tab: 文件权限审计
"""

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
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

from multi_system.system.security.file_audit import FileAuditor


def _fmt_size(b: int | float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


class FileAuditTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Path input ---
        top = QHBoxLayout()
        top.addWidget(QLabel("扫描路径:"))
        self._path_edit = QLineEdit("/")
        self._path_edit.setPlaceholderText("输入要审计的目录路径...")
        top.addWidget(self._path_edit)
        layout.addLayout(top)

        # --- Options ---
        opt_row = QHBoxLayout()
        self._world_writable_check = QCheckBox("检查 World-Writable")
        self._world_writable_check.setChecked(True)
        opt_row.addWidget(self._world_writable_check)
        self._suid_check = QCheckBox("检查 SUID 位")
        self._suid_check.setChecked(True)
        opt_row.addWidget(self._suid_check)
        opt_row.addWidget(QLabel("最大结果:"))
        self._limit_spin = QSpinBox()
        self._limit_spin.setRange(10, 10000)
        self._limit_spin.setValue(200)
        opt_row.addWidget(self._limit_spin)
        self._scan_btn = QPushButton("扫描")
        self._scan_btn.clicked.connect(self._scan)
        opt_row.addWidget(self._scan_btn)
        layout.addLayout(opt_row)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._scan)
        layout.addWidget(toolbar)

        # --- Result table ---
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["路径", "问题", "权限", "大小"])
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

    # --- Context menu ---

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)

        menu = QMenu(self)

        fix_action = menu.addAction("修复权限")
        fix_action.triggered.connect(lambda: self._fix_permission(row))

        menu.addSeparator()

        path_item = self._table.item(row, 0)
        path_text = path_item.text() if path_item else ""

        copy_path_action = menu.addAction("复制路径")
        copy_path_action.triggered.connect(lambda: self._copy_to_clipboard(path_text))

        open_dir_action = menu.addAction("在文件管理器中显示")
        open_dir_action.triggered.connect(lambda: self._open_in_file_manager(path_text))

        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)

    def _fix_permission(self, row: int):
        path_item = self._table.item(row, 0)
        issue_item = self._table.item(row, 1)
        if not path_item or not issue_item:
            return
        path = path_item.text()
        issue = issue_item.text()
        reply = QMessageBox.warning(
            self,
            "确认修复权限",
            f"确定要修复以下文件的权限吗？\n\n路径: {path}\n问题: {issue}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if FileAuditor.fix_permission(path, issue):
            QMessageBox.information(self, "成功", f"已修复 {path} 的权限")
            self._scan()
        else:
            QMessageBox.warning(self, "失败", f"无法修复 {path} 的权限，可能需要管理员权限")

    def _open_in_file_manager(self, path_str: str):
        if not path_str or not os.path.exists(path_str):
            QMessageBox.information(self, "提示", f"路径不存在: {path_str}")
            return
        try:
            if sys.platform == "linux":
                subprocess.Popen(["xdg-open", os.path.dirname(path_str)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", os.path.dirname(path_str)])
            elif sys.platform == "win32":
                subprocess.Popen(["explorer", "/select,", path_str])
        except (FileNotFoundError, OSError):
            QMessageBox.warning(self, "失败", "无法打开文件管理器")

    # --- Existing methods ---

    def _scan(self):
        path_str = self._path_edit.text().strip()
        if not path_str:
            return
        path = Path(path_str)
        if not path.exists():
            QMessageBox.warning(self, "错误", f"路径不存在: {path_str}")
            return

        check_world = self._world_writable_check.isChecked()
        check_suid = self._suid_check.isChecked()
        limit = self._limit_spin.value()

        self._scan_btn.setEnabled(False)
        self._status_label.setText("扫描中...")

        try:
            issues = FileAuditor.scan(
                path,
                check_world_writable=check_world,
                check_suid=check_suid,
                limit=limit,
            )
        except Exception as e:
            QMessageBox.warning(self, "错误", f"扫描失败: {e}")
            self._scan_btn.setEnabled(True)
            self._status_label.setText("")
            return

        self._table.setRowCount(0)
        for issue in issues:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(issue.path))
            self._table.setItem(row, 1, QTableWidgetItem(issue.issue))
            self._table.setItem(row, 2, QTableWidgetItem(issue.mode))
            self._table.setItem(row, 3, QTableWidgetItem(_fmt_size(issue.size)))

        self._status_label.setText(f"发现 {len(issues)} 个权限问题")
        self._scan_btn.setEnabled(True)
