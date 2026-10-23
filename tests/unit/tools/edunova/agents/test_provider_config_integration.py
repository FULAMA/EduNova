from pathlib import Path

from tools.edunova.agents.orchestration.config_loader import ProviderConfigLoader
from tools.edunova.agents.orchestration.registry import ProviderRegistry


def test_loaded_configs_can_be_registered(tmp_path: Path) -> None:
    config_file = tmp_path / "providers.json"
    config_file.write_text(
        """
        {
            "providers": [
                {
                    "name": "gemini",
                    "enabled": true,
                    "priority": 1,
                    "model": "test-model",
                    "timeout": 60
                },
                {
                    "name": "openrouter",
                    "enabled": true,
                    "priority": 2,
                    "model": "another-model",
                    "timeout": 120
                }
            ]
        }
        """,
        encoding="utf-8",
    )

    loader = ProviderConfigLoader()
    registry = ProviderRegistry()

    configs = loader.load(config_file)

    for config in configs:
        registry.register_config(config)

    assert registry.config_names() == ("gemini", "openrouter")
    assert registry.get_config("gemini").priority == 1
    assert registry.get_config("openrouter").priority == 2


def test_registered_config_controls_router_priority() -> None:
    registry = ProviderRegistry()

    registry.register_config(
        ProviderConfigLoader.config_type(
            name="gemini",
            priority=2,
        )
    )

    registry.register_config(
        ProviderConfigLoader.config_type(
            name="openrouter",
            priority=1,
        )
    )

    assert registry.config_names() == ("gemini", "openrouter")
