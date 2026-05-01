"""
Tab: 端口扫描
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.network.port_scanner import COMMON_PORTS, PortScanner


class PortScanTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._scanning = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._refresh)
        layout.addWidget(toolbar)

        # --- Host input ---
        host_row = QHBoxLayout()
        host_row.addWidget(QLabel("目标主机:"))
        self._host_edit = QLineEdit("127.0.0.1")
        self._host_edit.setPlaceholderText("IP 或域名")
        host_row.addWidget(self._host_edit)
        layout.addLayout(host_row)

        # --- Scan mode ---
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("扫描模式:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["常用端口", "指定范围"])
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_row.addWidget(self._mode_combo)
        layout.addLayout(mode_row)

        # --- Range inputs ---
        self._range_widget = QWidget()
        range_layout = QHBoxLayout(self._range_widget)
        range_layout.setContentsMargins(0, 0, 0, 0)
        range_layout.addWidget(QLabel("起始端口:"))
        self._port_start = QSpinBox()
        self._port_start.setRange(1, 65535)
        self._port_start.setValue(1)
        range_layout.addWidget(self._port_start)
        range_layout.addWidget(QLabel("结束端口:"))
        self._port_end = QSpinBox()
        self._port_end.setRange(1, 65535)
        self._port_end.setValue(1024)
        range_layout.addWidget(self._port_end)
        self._range_widget.setVisible(False)
        layout.addWidget(self._range_widget)

        # --- Scan button ---
        btn_row = QHBoxLayout()
        self._scan_btn = QPushButton("扫描")
        self._scan_btn.setFixedHeight(36)
        self._scan_btn.clicked.connect(self._on_scan)
        btn_row.addWidget(self._scan_btn)
        layout.addLayout(btn_row)

        # --- Progress ---
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # indeterminate
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # --- Result table ---
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["端口", "状态", "服务"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._table)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._refresh()

    def _on_mode_changed(self, index: int):
        self._range_widget.setVisible(index == 1)

    def _refresh(self):
        if not self._scanning:
            self._table.setRowCount(0)

    def _on_scan(self):
        if self._scanning:
            return

        host = self._host_edit.text().strip()
        if not host:
            return

        if self._mode_combo.currentIndex() == 0:
            ports = list(COMMON_PORTS.keys())
        else:
            start = self._port_start.value()
            end = self._port_end.value()
            if start > end:
                start, end = end, start
            ports = list(range(start, end + 1))

        self._scanning = True
        self._scan_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._table.setRowCount(0)

        QTimer.singleShot(0, lambda: self._do_scan(host, ports))

    def _do_scan(self, host: str, ports: list[int]):
        try:
            results = PortScanner.scan(host, ports)
        except Exception:
            results = []

        self._show_results(results)

    def _show_results(self, results):
        self._scanning = False
        self._scan_btn.setEnabled(True)
        self._progress.setVisible(False)

        self._table.setRowCount(0)
        # Show open ports first, then closed
        open_results = [r for r in results if r.is_open]
        closed_results = [r for r in results if not r.is_open]
        sorted_results = open_results + closed_results

        for r in sorted_results:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(str(r.port)))
            status = "开放" if r.is_open else "关闭"
            status_item = QTableWidgetItem(status)
            if r.is_open:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.gray)
            self._table.setItem(row, 1, status_item)
            self._table.setItem(row, 2, QTableWidgetItem(r.service))

        self._table.resizeColumnsToContents()

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)
        menu = QMenu(self)
        menu.addAction("复制端口号", self._copy_port)
        menu.addAction("复制服务名", self._copy_service)
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_port(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 0)
        if item:
            QApplication.clipboard().setText(item.text())

    def _copy_service(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 2)
        if item:
            QApplication.clipboard().setText(item.text())
