import json
from pathlib import Path

from tools.edunova.agents.orchestration.config import ProviderConfig


class ProviderConfigLoader:
    config_type = ProviderConfig

    def load(self, path: Path) -> tuple[ProviderConfig, ...]:
        if not path.exists():
            raise FileNotFoundError(path)

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON configuration.") from exc

        if not isinstance(data, dict):
            raise ValueError("Configuration root must be an object.")

        providers = data.get("providers")

        if not isinstance(providers, list):
            raise ValueError(
                "Configuration must contain a 'providers' list."
            )

        configs = []

        for provider in providers:
            if not isinstance(provider, dict):
                raise ValueError(
                    "Each provider configuration must be an object."
                )

            try:
                configs.append(ProviderConfig(**provider))
            except TypeError as exc:
                raise ValueError(
                    "Invalid provider configuration."
                ) from exc

        return tuple(configs)
