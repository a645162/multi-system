"""Claude Code 配置适配器"""
import json
import os
from pathlib import Path

from .ai_config import ModelProfile


class ClaudeCodeAdapter:
    CONFIG_PATH = Path.home() / ".claude" / "settings.json"

    @staticmethod
    def get_current() -> ModelProfile | None:
        env_key = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
        base_url = os.environ.get("ANTHROPIC_BASE_URL", "")
        model = os.environ.get("ANTHROPIC_MODEL", "")
        return ModelProfile(
            name="Claude Code (current)",
            tool="claude-code",
            provider="anthropic" if not base_url else "custom",
            model_id=model or "claude-sonnet-4-6",
            api_key_env="ANTHROPIC_AUTH_TOKEN" if env_key else "",
            base_url=base_url,
        )

    @staticmethod
    def apply(profile: ModelProfile) -> None:
        os.environ["ANTHROPIC_MODEL"] = profile.model_id
        if profile.base_url:
            os.environ["ANTHROPIC_BASE_URL"] = profile.base_url
        if profile.api_key_env:
            key = os.environ.get(profile.api_key_env, "")
            if key:
                os.environ["ANTHROPIC_AUTH_TOKEN"] = key

    @staticmethod
    def read_config() -> dict:
        if ClaudeCodeAdapter.CONFIG_PATH.exists():
            try:
                return json.loads(ClaudeCodeAdapter.CONFIG_PATH.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    @staticmethod
    def write_config(config: dict) -> None:
        ClaudeCodeAdapter.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        ClaudeCodeAdapter.CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
