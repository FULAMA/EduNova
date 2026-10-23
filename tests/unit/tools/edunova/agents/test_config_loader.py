import json
from pathlib import Path

from tools.edunova.agents.orchestration.config_loader import ProviderConfigLoader


def test_loader_reads_provider_configs(tmp_path: Path) -> None:
    config_file = tmp_path / "providers.json"
    config_file.write_text(
        json.dumps(
            {
                "providers": [
                    {
                        "name": "gemini",
                        "enabled": True,
                        "priority": 1,
                        "model": "test-model",
                        "timeout": 60,
                    },
                    {
                        "name": "openrouter",
                        "enabled": True,
                        "priority": 2,
                        "model": "another-model",
                        "timeout": 120,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    loader = ProviderConfigLoader()

    configs = loader.load(config_file)

    assert configs == (
        loader.config_type(
            name="gemini",
            enabled=True,
            priority=1,
            model="test-model",
            timeout=60,
        ),
        loader.config_type(
            name="openrouter",
            enabled=True,
            priority=2,
            model="another-model",
            timeout=120,
        ),
    )


def test_loader_rejects_missing_file(tmp_path: Path) -> None:
    loader = ProviderConfigLoader()

    try:
        loader.load(tmp_path / "missing.json")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")


def test_loader_rejects_invalid_json(tmp_path: Path) -> None:
    config_file = tmp_path / "providers.json"
    config_file.write_text("{invalid", encoding="utf-8")

    loader = ProviderConfigLoader()

    try:
        loader.load(config_file)
    except ValueError as exc:
        assert "json" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_loader_rejects_missing_providers_key(tmp_path: Path) -> None:
    config_file = tmp_path / "providers.json"
    config_file.write_text(
        json.dumps({"other": []}),
        encoding="utf-8",
    )

    loader = ProviderConfigLoader()

    try:
        loader.load(config_file)
    except ValueError as exc:
        assert "providers" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_loader_rejects_non_list_providers(tmp_path: Path) -> None:
    config_file = tmp_path / "providers.json"
    config_file.write_text(
        json.dumps({"providers": {}}),
        encoding="utf-8",
    )

    loader = ProviderConfigLoader()

    try:
        loader.load(config_file)
    except ValueError as exc:
        assert "providers" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")
def test_loader_rejects_non_object_provider(tmp_path: Path) -> None:
    config_file = tmp_path / "providers.json"
    config_file.write_text(
        json.dumps(
            {
                "providers": [
                    "gemini",
                ]
            }
        ),
        encoding="utf-8",
    )

    loader = ProviderConfigLoader()

    try:
        loader.load(config_file)
    except ValueError as exc:
        assert "provider" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_loader_rejects_provider_with_unknown_field(tmp_path: Path) -> None:
    config_file = tmp_path / "providers.json"
    config_file.write_text(
        json.dumps(
            {
                "providers": [
                    {
                        "name": "gemini",
                        "unknown": "field",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    loader = ProviderConfigLoader()

    try:
        loader.load(config_file)
    except ValueError as exc:
        assert "configuration" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")
