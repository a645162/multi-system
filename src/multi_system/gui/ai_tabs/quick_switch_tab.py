"""
Tab: 快捷切换 - AI模型快速切换
"""


from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.program.ai_models.ai_config import (
    SUPPORTED_TOOLS,
    TOOL_DISPLAY_NAMES,
)
from multi_system.program.ai_models.model_switcher import ModelSwitcher


class QuickSwitchTab(QWidget):
    def __init__(self):
        super().__init__()
        self._switcher: ModelSwitcher | None = None
        self._loaded = False
        self._tool_combos: dict[str, QComboBox] = {}
        self._result_labels: dict[str, QLabel] = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        layout.addWidget(toolbar)

        # Grid: for each tool, a row with combo + switch button + result label
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        header_label = QLabel("<b>工具</b>")
        profile_label = QLabel("<b>Profile</b>")
        action_label = QLabel("<b>操作</b>")
        result_label = QLabel("<b>状态</b>")
        grid.addWidget(header_label, 0, 0)
        grid.addWidget(profile_label, 0, 1)
        grid.addWidget(action_label, 0, 2)
        grid.addWidget(result_label, 0, 3)

        for row, tool in enumerate(SUPPORTED_TOOLS, start=1):
            display = TOOL_DISPLAY_NAMES.get(tool, tool)

            tool_label = QLabel(display)
            tool_label.setFixedWidth(100)
            grid.addWidget(tool_label, row, 0)

            combo = QComboBox()
            combo.setMinimumWidth(250)
            self._tool_combos[tool] = combo
            grid.addWidget(combo, row, 1)

            btn = QPushButton("切换")
            btn.setFixedWidth(70)
            btn.clicked.connect(lambda checked, t=tool: self._switch_profile(t))
            grid.addWidget(btn, row, 2)

            result = QLabel("-")
            result.setMinimumWidth(200)
            self._result_labels[tool] = result
            grid.addWidget(result, row, 3)

        layout.addLayout(grid)
        layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._switcher = ModelSwitcher()
            self._refresh_combos()

    def _force_refresh(self):
        if self._switcher:
            self._switcher = ModelSwitcher()
        self._refresh_combos()

    def _refresh_combos(self):
        if not self._switcher:
            return
        profiles = self._switcher.load_profiles()
        current_all = self._switcher.get_all_current()

        for tool in SUPPORTED_TOOLS:
            combo = self._tool_combos[tool]
            result_label = self._result_labels[tool]
            combo.clear()

            # Add current config as first item
            current = current_all.get(tool)
            if current:
                combo.addItem(f"[当前] {current.model_id or '-'}", userData=None)
            else:
                combo.addItem("[当前] 未检测到", userData=None)

            # Add saved profiles for this tool
            tool_profiles = [p for p in profiles if p.tool == tool]
            for p in tool_profiles:
                display = f"{p.name} ({p.model_id})"
                combo.addItem(display, userData=p)

            # Update result label
            if current and current.model_id:
                result_label.setText(f"当前: {current.model_id}")
            else:
                result_label.setText("当前: -")

    def _switch_profile(self, tool: str):
        if not self._switcher:
            return
        combo = self._tool_combos.get(tool)
        result_label = self._result_labels.get(tool)
        if not combo or not result_label:
            return

        profile = combo.currentData()
        if profile is None:
            result_label.setText("已是当前配置，无需切换")
            return

        self._switcher.apply_profile(profile)
        display = TOOL_DISPLAY_NAMES.get(tool, tool)
        result_label.setText(f"已切换: {profile.model_id}")
        QMessageBox.information(
            self, "切换成功",
            f"{display} 已切换到 \"{profile.name}\" ({profile.model_id})",
        )
