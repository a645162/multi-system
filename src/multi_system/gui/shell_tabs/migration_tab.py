"""
Tab: 配置迁移
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.system.shells.migration import MigrationEntry, MigrationManager


class _PreviewDialog(QDialog):
    def __init__(self, content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("迁移预览")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)
        editor = QPlainTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(content)
        layout.addWidget(editor)

        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)


class MigrationTab(QWidget):
    def __init__(self):
        super().__init__()
        self._manager: MigrationManager | None = None
        self._entries: list[MigrationEntry] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Source → Target
        top = QHBoxLayout()
        top.addWidget(QLabel("源 Shell:"))
        self._source_combo = QComboBox()
        self._source_combo.addItems(["bash", "zsh"])
        top.addWidget(self._source_combo)

        top.addWidget(QLabel("→"))
        self._target_combo = QComboBox()
        self._target_combo.addItems(["zsh", "bash"])
        self._target_combo.setCurrentText("zsh")
        top.addWidget(self._target_combo)
        top.addStretch()
        layout.addLayout(top)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("分析", self._analyze)
        toolbar.addAction("预览迁移内容", self._preview)
        toolbar.addAction("执行迁移", self._execute)
        layout.addWidget(toolbar)

        # Table
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["类型", "名称", "值", "可迁移"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

    def _analyze(self):
        src = self._source_combo.currentText()
        tgt = self._target_combo.currentText()
        if src == tgt:
            QMessageBox.warning(self, "错误", "源和目标 Shell 不能相同")
            return
        self._manager = MigrationManager(src, tgt)
        self._entries = self._manager.analyze()
        self._table.setRowCount(0)
        for e in self._entries:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(e.category))
            self._table.setItem(row, 1, QTableWidgetItem(e.name))
            self._table.setItem(row, 2, QTableWidgetItem(e.value))
            self._table.setItem(row, 3, QTableWidgetItem("✓" if e.migratable else "✗"))

    def _preview(self):
        if not self._manager or not self._entries:
            QMessageBox.information(self, "提示", "请先分析")
            return
        migratable = [e for e in self._entries if e.migratable]
        content = self._manager.generate_migration(migratable)
        dlg = _PreviewDialog(content, self)
        dlg.exec()

    def _execute(self):
        if not self._manager or not self._entries:
            QMessageBox.information(self, "提示", "请先分析")
            return
        migratable = [e for e in self._entries if e.migratable]
        if not migratable:
            QMessageBox.information(self, "提示", "没有可迁移的配置")
            return
        reply = QMessageBox.warning(
            self, "确认迁移",
            f"将迁移 {len(migratable)} 项到 {self._target_combo.currentText()}，是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._manager.execute(migratable)
            QMessageBox.information(self, "迁移完成", "配置已迁移，重新打开终端即可生效")
