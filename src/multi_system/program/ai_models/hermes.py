"""Hermes 配置适配器"""
from pathlib import Path

from .ai_config import ModelProfile


class HermesAdapter:
    CONFIG_PATH = Path.home() / ".hermes" / "config.yaml"

    @staticmethod
    def get_current() -> ModelProfile | None:
        if not HermesAdapter.CONFIG_PATH.exists():
            return None
        try:
            import yaml
            config = yaml.safe_load(HermesAdapter.CONFIG_PATH.read_text(encoding="utf-8"))
            model_cfg = config.get("model", {}) if config else {}
            return ModelProfile(
                name="Hermes (current)",
                tool="hermes",
                provider=model_cfg.get("provider", ""),
                model_id=model_cfg.get("default", ""),
                base_url=model_cfg.get("base_url", ""),
            )
        except (OSError, ImportError):
            return None

    @staticmethod
    def apply(profile: ModelProfile) -> None:
        if not HermesAdapter.CONFIG_PATH.exists():
            return
        try:
            import yaml
            config = yaml.safe_load(HermesAdapter.CONFIG_PATH.read_text(encoding="utf-8"))
            if config is None:
                config = {}
            if "model" not in config:
                config["model"] = {}
            config["model"]["default"] = profile.model_id
            config["model"]["provider"] = profile.provider
            if profile.base_url:
                config["model"]["base_url"] = profile.base_url
            HermesAdapter.CONFIG_PATH.write_text(
                yaml.dump(config, allow_unicode=True, default_flow_style=False),
                encoding="utf-8",
            )
        except (OSError, ImportError):
            pass
