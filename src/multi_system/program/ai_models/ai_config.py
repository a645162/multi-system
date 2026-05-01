"""AI模型统一配置数据类"""
from dataclasses import dataclass, field


@dataclass
class ModelProfile:
    name: str
    tool: str  # "claude-code" | "codex" | "opencode" | "openclaw" | "hermes"
    provider: str = ""
    model_id: str = ""
    api_key_env: str = ""  # env var name holding the API key
    base_url: str = ""
    extra: dict = field(default_factory=dict)

SUPPORTED_TOOLS = ["claude-code", "codex", "opencode", "openclaw", "hermes"]

TOOL_DISPLAY_NAMES = {
    "claude-code": "Claude Code",
    "codex": "Codex",
    "opencode": "OpenCode",
    "openclaw": "OpenClaw",
    "hermes": "Hermes",
}
