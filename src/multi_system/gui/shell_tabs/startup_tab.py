"""
Tab: 启动速度分析
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.system.shells.startup import StartupAnalyzer


class StartupTab(QWidget):
    def __init__(self):
        super().__init__()
        self._analyzer: StartupAnalyzer | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Shell selector + count
        top = QHBoxLayout()
        top.addWidget(QLabel("Shell:"))
        self._shell_combo = QComboBox()
        self._shell_combo.addItems(["bash", "zsh"])
        self._shell_combo.currentTextChanged.connect(self._on_shell_changed)
        top.addWidget(self._shell_combo)

        top.addWidget(QLabel("测量次数:"))
        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 20)
        self._count_spin.setValue(3)
        top.addWidget(self._count_spin)
        top.addStretch()
        layout.addLayout(top)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("测量", self._measure)
        toolbar.addAction("Zsh Profiling", self._zprof)
        layout.addWidget(toolbar)

        # Results
        self._result_label = QLabel("点击「测量」开始分析")
        layout.addWidget(self._result_label)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["次数", "Real (s)", "User (s)", "Sys (s)"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table)

        # Profiling output
        layout.addWidget(QLabel("Zsh Profiling 输出:"))
        self._prof_output = QPlainTextEdit()
        self._prof_output.setReadOnly(True)
        self._prof_output.setMaximumHeight(200)
        layout.addWidget(self._prof_output)

    def _on_shell_changed(self, shell: str):
        self._analyzer = StartupAnalyzer(shell)
        self._table.setRowCount(0)
        self._result_label.setText("点击「测量」开始分析")

    def _measure(self):
        if not self._analyzer:
            return
        count = self._count_spin.value()
        self._table.setRowCount(0)
        results = self._analyzer.measure_multiple(count)

        total_real = 0.0
        for i, r in enumerate(results, 1):
            if r.real_time < 0:
                self._result_label.setText("测量失败，请确认 shell 可用")
                return
            total_real += r.real_time
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(str(i)))
            self._table.setItem(row, 1, QTableWidgetItem(f"{r.real_time:.3f}"))
            self._table.setItem(row, 2, QTableWidgetItem(f"{r.user_time:.3f}"))
            self._table.setItem(row, 3, QTableWidgetItem(f"{r.sys_time:.3f}"))

        avg = total_real / count
        self._result_label.setText(f"平均启动时间: {avg:.3f}s ({count} 次测量)")

    def _zprof(self):
        if not self._analyzer or self._analyzer.shell != "zsh":
            QMessageBox.information(self, "提示", "Zsh Profiling 仅支持 zsh")
            return
        self.statusBar().showMessage("正在测量...") if hasattr(self, 'statusBar') else None
        result, prof_lines = self._analyzer.measure_zsh_with_profiling()
        self._prof_output.setPlainText("\n".join(prof_lines) if prof_lines else "无 profiling 数据")
        self._result_label.setText(f"Zsh 启动时间: {result.real_time:.3f}s")
