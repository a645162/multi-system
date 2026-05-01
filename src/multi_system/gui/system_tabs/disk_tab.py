"""
Tab: 磁盘分析
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
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
        self._dir_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._dir_table)

        layout.addWidget(QLabel("大文件 (>100MB):"))
        self._file_table = QTableWidget(0, 2)
        self._file_table.setHorizontalHeaderLabels(["文件", "大小"])
        self._file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
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
