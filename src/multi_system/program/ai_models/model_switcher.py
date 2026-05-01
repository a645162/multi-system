"""统一模型切换器"""
from multi_system.core.data_manager import DataManager

from .ai_config import SUPPORTED_TOOLS, ModelProfile
from .claude_code import ClaudeCodeAdapter
from .codex import CodexAdapter
from .hermes import HermesAdapter
from .openclaw import OpenClawAdapter
from .opencode import OpenCodeAdapter

ADAPTERS = {
    "claude-code": ClaudeCodeAdapter,
    "codex": CodexAdapter,
    "opencode": OpenCodeAdapter,
    "openclaw": OpenClawAdapter,
    "hermes": HermesAdapter,
}

class ModelSwitcher:
    def __init__(self):
        self._dm = DataManager()
        self._profiles_file = self._dm.get_data_dir("ai_models") / "profiles.toml"

    def get_current(self, tool: str) -> ModelProfile | None:
        adapter = ADAPTERS.get(tool)
        return adapter.get_current() if adapter else None

    def get_all_current(self) -> dict[str, ModelProfile | None]:
        return {tool: self.get_current(tool) for tool in SUPPORTED_TOOLS}

    def apply_profile(self, profile: ModelProfile) -> None:
        adapter = ADAPTERS.get(profile.tool)
        if adapter:
            adapter.apply(profile)

    def save_profiles(self, profiles: list[ModelProfile]) -> None:
        from dataclasses import asdict
        data = {"profiles": [{k: v for k, v in asdict(p).items() if k != "extra" or v} for p in profiles]}
        self._dm.save_toml(self._profiles_file, data)

    def load_profiles(self) -> list[ModelProfile]:
        data = self._dm.load_toml(self._profiles_file)
        profiles = []
        for item in data.get("profiles", []):
            profiles.append(ModelProfile(**{k: v for k, v in item.items() if k in ModelProfile.__dataclass_fields__}))
        return profiles

    @staticmethod
    def launch_tool(tool: str) -> None:
        import subprocess
        cmd_map = {
            "claude-code": ["claude"],
            "codex": ["codex"],
            "opencode": ["opencode"],
            "openclaw": ["openclaw"],
            "hermes": ["hermes"],
        }
        cmd = cmd_map.get(tool)
        if cmd:
            subprocess.Popen(cmd, start_new_session=True)
