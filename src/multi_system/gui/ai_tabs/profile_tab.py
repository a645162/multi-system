"""
Tab: 配置管理 - AI模型Profile管理
"""


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
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

from multi_system.program.ai_models.ai_config import (
    SUPPORTED_TOOLS,
    TOOL_DISPLAY_NAMES,
    ModelProfile,
)
from multi_system.program.ai_models.model_switcher import ModelSwitcher


class _AddProfileDialog(QDialog):
    def __init__(self, parent=None, profile: ModelProfile | None = None):
        super().__init__(parent)
        self.setWindowTitle("编辑 Profile" if profile else "添加 Profile")
        self.setMinimumWidth(450)

        layout = QFormLayout(self)

        self.name_edit = QLineEdit(profile.name if profile else "")
        self.tool_combo = QComboBox()
        self.tool_combo.addItems([TOOL_DISPLAY_NAMES.get(t, t) for t in SUPPORTED_TOOLS])
        if profile and profile.tool in SUPPORTED_TOOLS:
            self.tool_combo.setCurrentIndex(SUPPORTED_TOOLS.index(profile.tool))
        self.provider_edit = QLineEdit(profile.provider if profile else "")
        self.model_id_edit = QLineEdit(profile.model_id if profile else "")
        self.api_key_env_edit = QLineEdit(profile.api_key_env if profile else "")
        self.base_url_edit = QLineEdit(profile.base_url if profile else "")

        layout.addRow("名称:", self.name_edit)
        layout.addRow("工具:", self.tool_combo)
        layout.addRow("Provider:", self.provider_edit)
        layout.addRow("Model ID:", self.model_id_edit)
        layout.addRow("API Key Env:", self.api_key_env_edit)
        layout.addRow("Base URL:", self.base_url_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_profile(self) -> ModelProfile:
        tool = SUPPORTED_TOOLS[self.tool_combo.currentIndex()]
        return ModelProfile(
            name=self.name_edit.text().strip(),
            tool=tool,
            provider=self.provider_edit.text().strip(),
            model_id=self.model_id_edit.text().strip(),
            api_key_env=self.api_key_env_edit.text().strip(),
            base_url=self.base_url_edit.text().strip(),
        )


class ProfileTab(QWidget):
    def __init__(self):
        super().__init__()
        self._switcher: ModelSwitcher | None = None
        self._profiles: list[ModelProfile] = []
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Top: tool selector + current config info
        top = QHBoxLayout()
        top.addWidget(QLabel("工具:"))
        self._tool_combo = QComboBox()
        self._tool_combo.addItems([TOOL_DISPLAY_NAMES.get(t, t) for t in SUPPORTED_TOOLS])
        self._tool_combo.currentIndexChanged.connect(self._on_tool_changed)
        top.addWidget(self._tool_combo)
        top.addStretch()
        layout.addLayout(top)

        # Current config label
        self._current_label = QLabel("当前配置: -")
        self._current_label.setWordWrap(True)
        layout.addWidget(self._current_label)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addSeparator()
        toolbar.addAction("添加Profile", self._add_profile)
        toolbar.addAction("删除Profile", self._delete_profile)
        toolbar.addSeparator()
        toolbar.addAction("应用Profile", self._apply_profile)
        toolbar.addAction("启动工具", self._launch_tool)
        layout.addWidget(toolbar)

        # Profiles table
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(["名称", "工具", "Provider", "Model ID", "API Key Env", "Base URL"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._switcher = ModelSwitcher()
            self._on_tool_changed(self._tool_combo.currentIndex())

    def _on_tool_changed(self, index: int):
        if not self._switcher:
            return
        tool = SUPPORTED_TOOLS[index] if 0 <= index < len(SUPPORTED_TOOLS) else ""
        self._update_current_info(tool)
        self._refresh_table()

    def _update_current_info(self, tool: str):
        profile = self._switcher.get_current(tool) if self._switcher else None
        if profile:
            parts = [f"Model: {profile.model_id}"]
            if profile.provider:
                parts.append(f"Provider: {profile.provider}")
            if profile.base_url:
                parts.append(f"Base URL: {profile.base_url}")
            self._current_label.setText("当前配置: " + " | ".join(parts))
        else:
            self._current_label.setText("当前配置: 未检测到配置")

    def _force_refresh(self):
        if self._switcher:
            self._switcher = ModelSwitcher()
        tool = SUPPORTED_TOOLS[self._tool_combo.currentIndex()]
        self._update_current_info(tool)
        self._refresh_table()

    def _refresh_table(self):
        if not self._switcher:
            return
        self._profiles = self._switcher.load_profiles()
        self._table.setRowCount(0)
        for profile in self._profiles:
            row = self._table.rowCount()
            self._table.insertRow(row)
            values = [
                profile.name,
                TOOL_DISPLAY_NAMES.get(profile.tool, profile.tool),
                profile.provider,
                profile.model_id,
                profile.api_key_env,
                profile.base_url,
            ]
            for col, text in enumerate(values):
                item = QTableWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, row)
                self._table.setItem(row, col, item)

    def _selected_profile(self) -> ModelProfile | None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return None
        idx = rows[0].row()
        if 0 <= idx < len(self._profiles):
            return self._profiles[idx]
        return None

    def _add_profile(self):
        if not self._switcher:
            return
        dlg = _AddProfileDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            profile = dlg.get_profile()
            if not profile.name:
                return
            self._profiles.append(profile)
            self._switcher.save_profiles(self._profiles)
            self._refresh_table()

    def _delete_profile(self):
        if not self._switcher:
            return
        profile = self._selected_profile()
        if profile is None:
            return
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 Profile \"{profile.name}\" 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._profiles.remove(profile)
            self._switcher.save_profiles(self._profiles)
            self._refresh_table()

    def _apply_profile(self):
        if not self._switcher:
            return
        profile = self._selected_profile()
        if profile is None:
            QMessageBox.warning(self, "提示", "请先选择一个 Profile")
            return
        self._switcher.apply_profile(profile)
        self._switcher.save_profiles(self._profiles)
        tool = SUPPORTED_TOOLS[self._tool_combo.currentIndex()]
        self._update_current_info(tool)
        QMessageBox.information(self, "应用成功", f"已应用 Profile \"{profile.name}\"")

    def _launch_tool(self):
        if not self._switcher:
            return
        tool = SUPPORTED_TOOLS[self._tool_combo.currentIndex()]
        try:
            ModelSwitcher.launch_tool(tool)
        except FileNotFoundError:
            QMessageBox.warning(
                self, "启动失败",
                f"未找到 {TOOL_DISPLAY_NAMES.get(tool, tool)} 的可执行文件，请确认已安装。",
            )
