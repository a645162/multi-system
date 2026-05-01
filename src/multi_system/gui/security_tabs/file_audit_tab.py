"""
Tab: 文件权限审计
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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
        self._table.horizontalHeader().setStretchLastSection(True)
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
