"""OpenClaw 配置适配器"""
import json
from pathlib import Path

from .ai_config import ModelProfile


class OpenClawAdapter:
    CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

    @staticmethod
    def get_current() -> ModelProfile | None:
        if not OpenClawAdapter.CONFIG_PATH.exists():
            return None
        try:
            config = json.loads(OpenClawAdapter.CONFIG_PATH.read_text(encoding="utf-8"))
            model_cfg = config.get("agents", {}).get("defaults", {}).get("model", {})
            primary = model_cfg.get("primary", "")
            provider = primary.split("/")[0] if "/" in primary else ""
            model_id = primary.split("/", 1)[1] if "/" in primary else primary
            return ModelProfile(
                name="OpenClaw (current)",
                tool="openclaw",
                provider=provider,
                model_id=model_id,
            )
        except (json.JSONDecodeError, OSError):
            return None

    @staticmethod
    def apply(profile: ModelProfile) -> None:
        if not OpenClawAdapter.CONFIG_PATH.exists():
            return
        try:
            config = json.loads(OpenClawAdapter.CONFIG_PATH.read_text(encoding="utf-8"))
            if "agents" not in config:
                config["agents"] = {}
            if "defaults" not in config["agents"]:
                config["agents"]["defaults"] = {}
            if "model" not in config["agents"]["defaults"]:
                config["agents"]["defaults"]["model"] = {}
            primary = f"{profile.provider}/{profile.model_id}" if profile.provider else profile.model_id
            config["agents"]["defaults"]["model"]["primary"] = primary
            OpenClawAdapter.CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        except (json.JSONDecodeError, OSError):
            pass
