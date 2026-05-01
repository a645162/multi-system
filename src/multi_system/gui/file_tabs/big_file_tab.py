"""
Tab: 大文件查找
"""

from pathlib import Path

from PySide6.QtWidgets import (
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
