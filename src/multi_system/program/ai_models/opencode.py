"""OpenCode 配置适配器"""
import json
from pathlib import Path

from .ai_config import ModelProfile


class OpenCodeAdapter:
    CONFIG_PATH = Path.home() / ".config" / "opencode" / "opencode.json"

    @staticmethod
    def get_current() -> ModelProfile | None:
        if not OpenCodeAdapter.CONFIG_PATH.exists():
            return None
        try:
            config = json.loads(OpenCodeAdapter.CONFIG_PATH.read_text(encoding="utf-8"))
            model = config.get("model", "")
            provider = model.split("/")[0] if "/" in model else ""
            model_id = model.split("/", 1)[1] if "/" in model else model
            return ModelProfile(
                name="OpenCode (current)",
                tool="opencode",
                provider=provider,
                model_id=model_id,
            )
        except (json.JSONDecodeError, OSError):
            return None

    @staticmethod
    def apply(profile: ModelProfile) -> None:
        if not OpenCodeAdapter.CONFIG_PATH.exists():
            return
        try:
            config = json.loads(OpenCodeAdapter.CONFIG_PATH.read_text(encoding="utf-8"))
            config["model"] = f"{profile.provider}/{profile.model_id}" if profile.provider else profile.model_id
            OpenCodeAdapter.CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        except (json.JSONDecodeError, OSError):
            pass
