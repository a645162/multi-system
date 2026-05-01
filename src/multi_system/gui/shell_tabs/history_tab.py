"""
Tab: 历史记录分析
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.core.data_manager import DataManager
from multi_system.system.shells.history import HistoryAnalyzer


class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self._analyzer: HistoryAnalyzer | None = None
        self._dm = DataManager()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Shell selector + search
        top = QHBoxLayout()
        top.addWidget(QLabel("Shell:"))
        self._shell_combo = QComboBox()
        self._shell_combo.addItems(["bash", "zsh"])
        self._shell_combo.currentTextChanged.connect(self._on_shell_changed)
        top.addWidget(self._shell_combo)

        top.addWidget(QLabel("搜索:"))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("输入关键词过滤...")
        self._search_edit.textChanged.connect(self._on_search)
        top.addWidget(self._search_edit)
        layout.addLayout(top)

        # Stats
        self._stats_label = QLabel("选择 Shell 后查看统计")
        layout.addWidget(self._stats_label)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._refresh)
        toolbar.addAction("导出 TOML", self._export_toml)
        layout.addWidget(toolbar)

        # Table
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["排名", "命令", "次数"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

    def _on_shell_changed(self, shell: str):
        self._analyzer = HistoryAnalyzer(shell)
        self._refresh()

    def _refresh(self):
        if not self._analyzer:
            return
        stats = self._analyzer.stats()
        self._stats_label.setText(
            f"总命令: {stats.total}  |  唯一命令: {stats.unique}"
        )
        self._search_edit.clear()
        self._show_top(stats.top)

    def _show_top(self, items: list[tuple[str, int]]):
        self._table.setRowCount(0)
        for rank, (cmd, count) in enumerate(items, 1):
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(str(rank)))
            self._table.setItem(row, 1, QTableWidgetItem(cmd))
            self._table.setItem(row, 2, QTableWidgetItem(str(count)))

    def _on_search(self, keyword: str):
        if not self._analyzer:
            return
        if not keyword:
            self._refresh()
            return
        results = self._analyzer.search(keyword)
        self._table.setRowCount(0)
        for i, cmd in enumerate(results[:100], 1):
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(str(i)))
            self._table.setItem(row, 1, QTableWidgetItem(cmd))
            self._table.setItem(row, 2, QTableWidgetItem(""))

    def _export_toml(self):
        if not self._analyzer:
            return
        stats = self._analyzer.stats()
        data = {
            "shell": self._analyzer.shell,
            "total": stats.total,
            "unique": stats.unique,
            "top_commands": [{"command": c, "count": n} for c, n in stats.top],
        }
        out = self._dm.get_data_dir("shell") / "history_export.toml"
        self._dm.save_toml(out, data)
        QMessageBox.information(self, "导出成功", f"已导出到 {out}")
