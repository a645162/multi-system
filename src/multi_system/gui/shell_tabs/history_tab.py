"""
Tab: 历史记录分析
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.core.data_manager import DataManager
from multi_system.system.shells.aliases import AliasManager
from multi_system.system.shells.history import HistoryAnalyzer


class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self._analyzer: HistoryAnalyzer | None = None
        self._dm = DataManager()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

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

        self._stats_label = QLabel("选择 Shell 后查看统计")
        layout.addWidget(self._stats_label)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addAction("导出 TOML", self._export_toml)
        layout.addWidget(toolbar)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["排名", "命令", "次数"])
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
            self._on_shell_changed(self._shell_combo.currentText())

    def _on_shell_changed(self, shell: str):
        self._analyzer = HistoryAnalyzer(shell)
        self._refresh()

    def _force_refresh(self):
        self._on_shell_changed(self._shell_combo.currentText())

    def _refresh(self):
        if not self._analyzer:
            return

        self._progress.setVisible(True)
        self._progress.setRange(0, 0)  # indeterminate

        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, self._do_refresh)

    def _do_refresh(self):
        stats = self._analyzer.stats()
        self._stats_label.setText(
            f"总命令: {stats.total}  |  唯一命令: {stats.unique}"
        )
        self._search_edit.clear()
        self._show_top(stats.top)
        self._progress.setVisible(False)

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

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)
        menu = QMenu(self)
        menu.addAction("复制命令", self._copy_command)
        menu.addAction("添加为 Alias", self._add_as_alias)
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_command(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 1)
        if item:
            QApplication.clipboard().setText(item.text())

    def _add_as_alias(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return
        item = self._table.item(rows[0].row(), 1)
        if not item:
            return
        command = item.text()
        name, ok = QInputDialog.getText(
            self, "添加 Alias", f"为命令添加 Alias 名称:\n\n命令: {command}"
        )
        if ok and name.strip():
            shell = self._shell_combo.currentText()
            mgr = AliasManager(shell)
            mgr.add_alias(name.strip(), command)
            QMessageBox.information(self, "添加成功", f"已添加 alias: {name.strip()}={command}")
