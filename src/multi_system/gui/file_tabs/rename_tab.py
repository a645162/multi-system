"""
Tab: 批量重命名
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
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

from multi_system.files.batch_rename import execute_rename, preview_rename


class RenameTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Directory ---
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("目录:"))
        self._dir_edit = QLineEdit()
        self._dir_edit.setPlaceholderText("输入目录路径...")
        dir_row.addWidget(self._dir_edit)
        layout.addLayout(dir_row)

        # --- Pattern / Replacement ---
        pat_row = QHBoxLayout()
        pat_row.addWidget(QLabel("查找:"))
        self._pattern_edit = QLineEdit()
        self._pattern_edit.setPlaceholderText("要替换的文本或正则表达式...")
        pat_row.addWidget(self._pattern_edit)
        pat_row.addWidget(QLabel("替换为:"))
        self._replacement_edit = QLineEdit()
        self._replacement_edit.setPlaceholderText("替换后的文本...")
        pat_row.addWidget(self._replacement_edit)
        layout.addLayout(pat_row)

        # --- Options ---
        opt_row = QHBoxLayout()
        self._regex_check = QCheckBox("使用正则表达式")
        opt_row.addWidget(self._regex_check)
        opt_row.addStretch()
        layout.addLayout(opt_row)

        # --- Buttons ---
        btn_row = QHBoxLayout()
        self._preview_btn = QPushButton("预览")
        self._preview_btn.clicked.connect(self._preview)
        btn_row.addWidget(self._preview_btn)
        self._execute_btn = QPushButton("执行重命名")
        self._execute_btn.clicked.connect(self._execute)
        self._execute_btn.setEnabled(False)
        btn_row.addWidget(self._execute_btn)
        layout.addLayout(btn_row)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._preview)
        layout.addWidget(toolbar)

        # --- Preview table ---
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["原文件名", "新文件名"])
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
            self._preview()

    def _preview(self):
        dir_str = self._dir_edit.text().strip()
        pattern = self._pattern_edit.text()
        replacement = self._replacement_edit.text()
        if not dir_str or not pattern:
            self._table.setRowCount(0)
            self._status_label.setText("")
            return

        directory = Path(dir_str)
        if not directory.is_dir():
            QMessageBox.warning(self, "错误", f"目录不存在: {dir_str}")
            return

        use_regex = self._regex_check.isChecked()
        ops = preview_rename(directory, pattern, replacement, regex=use_regex)

        self._table.setRowCount(0)
        for op in ops:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(str(op.old_path)))
            self._table.setItem(row, 1, QTableWidgetItem(str(op.new_path)))

        self._execute_btn.setEnabled(len(ops) > 0)
        self._status_label.setText(f"预览: {len(ops)} 个文件将被重命名")

    def _execute(self):
        dir_str = self._dir_edit.text().strip()
        pattern = self._pattern_edit.text()
        replacement = self._replacement_edit.text()
        if not dir_str or not pattern:
            return

        directory = Path(dir_str)
        use_regex = self._regex_check.isChecked()
        ops = preview_rename(directory, pattern, replacement, regex=use_regex)
        if not ops:
            return

        reply = QMessageBox.warning(
            self,
            "确认执行",
            f"确定要重命名 {len(ops)} 个文件吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success = execute_rename(ops)
        QMessageBox.information(self, "完成", f"成功重命名 {success}/{len(ops)} 个文件")
        self._execute_btn.setEnabled(False)
        self._preview()

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)
        menu = QMenu(self)
        menu.addAction("复制原文件名", self._copy_old_name)
        menu.addAction("复制新文件名", self._copy_new_name)
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_old_name(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 0)
        if item:
            QApplication.clipboard().setText(item.text())

    def _copy_new_name(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 1)
        if item:
            QApplication.clipboard().setText(item.text())
