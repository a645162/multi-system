"""Codex 配置适配器"""
import os
from pathlib import Path

from .ai_config import ModelProfile


class CodexAdapter:
    CONFIG_PATH = Path.home() / ".codex" / "config.toml"

    @staticmethod
    def get_current() -> ModelProfile | None:
        model = os.environ.get("OPENAI_MODEL", "")
        base_url = os.environ.get("OPENAI_BASE_URL", "")
        key_env = "OPENAI_API_KEY" if os.environ.get("OPENAI_API_KEY") else ""
        return ModelProfile(
            name="Codex (current)",
            tool="codex",
            provider="openai" if not base_url else "custom",
            model_id=model or "codex-mini",
            api_key_env=key_env,
            base_url=base_url,
        )

    @staticmethod
    def apply(profile: ModelProfile) -> None:
        os.environ["OPENAI_MODEL"] = profile.model_id
        if profile.base_url:
            os.environ["OPENAI_BASE_URL"] = profile.base_url
        if profile.api_key_env:
            key = os.environ.get(profile.api_key_env, "")
            if key:
                os.environ["OPENAI_API_KEY"] = key
