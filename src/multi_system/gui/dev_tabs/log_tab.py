"""
Tab: 日志查看器
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.program.log_viewer import LogViewer


class LogTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Log file selector ---
        file_row = QHBoxLayout()
        file_row.addWidget(QLabel("日志文件:"))
        self._log_combo = QComboBox()
        self._log_combo.setMinimumWidth(300)
        file_row.addWidget(self._log_combo)
        self._browse_btn = QPushButton("浏览...")
        self._browse_btn.clicked.connect(self._browse_file)
        file_row.addWidget(self._browse_btn)
        layout.addLayout(file_row)

        # --- Search ---
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("搜索:"))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("关键词过滤...")
        self._search_edit.returnPressed.connect(self._search)
        search_row.addWidget(self._search_edit)
        self._search_btn = QPushButton("搜索")
        self._search_btn.clicked.connect(self._search)
        search_row.addWidget(self._search_btn)
        layout.addLayout(search_row)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._refresh)
        layout.addWidget(toolbar)

        # --- Content view ---
        self._content = QPlainTextEdit()
        self._content.setReadOnly(True)
        self._content.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self._content)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._populate_log_files()
            self._refresh()

    def _populate_log_files(self):
        self._log_combo.clear()
        logs = LogViewer.get_common_logs()
        for p in logs:
            self._log_combo.addItem(str(p), str(p))

    def _browse_file(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "选择日志文件", "/", "All Files (*)")
        if path:
            self._log_combo.addItem(path, path)
            self._log_combo.setCurrentIndex(self._log_combo.count() - 1)
            self._refresh()

    def _refresh(self):
        path_str = self._log_combo.currentData()
        if not path_str:
            self._content.clear()
            return
        path = Path(path_str)
        content = LogViewer.read_tail(path)
        self._content.setPlainText(content)

    def _search(self):
        path_str = self._log_combo.currentData()
        keyword = self._search_edit.text().strip()
        if not path_str or not keyword:
            return
        path = Path(path_str)
        results = LogViewer.search(path, keyword)
        self._content.setPlainText("\n".join(results))
