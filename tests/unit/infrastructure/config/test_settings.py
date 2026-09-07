import pytest

from src.infrastructure.config.settings import (
    DEVELOPMENT_JWT_SECRET,
    Settings,
)


def test_development_uses_default_jwt_secret(monkeypatch):
    monkeypatch.delenv("EDUNOVA_JWT_SECRET", raising=False)
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "development")

    settings = Settings.from_environment()

    assert settings.environment == "development"
    assert settings.jwt_secret
    assert settings.access_token_expire_minutes == 15
    assert settings.refresh_token_expire_days == 7
    assert settings.database_path == "edunova.db"


def test_test_environment_uses_default_jwt_secret(monkeypatch):
    monkeypatch.delenv("EDUNOVA_JWT_SECRET", raising=False)
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "test")

    settings = Settings.from_environment()

    assert settings.environment == "test"
    assert settings.jwt_secret


def test_production_requires_jwt_secret(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "production")
    monkeypatch.delenv("EDUNOVA_JWT_SECRET", raising=False)

    with pytest.raises(
        ValueError,
        match="EDUNOVA_JWT_SECRET",
    ):
        Settings.from_environment()


def test_environment_variables_are_used(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "production")
    monkeypatch.setenv(
        "EDUNOVA_JWT_SECRET",
        "production-super-secret-key-of-64-characters-minimum-length-ok",
    )
    monkeypatch.setenv(
        "EDUNOVA_ACCESS_TOKEN_EXPIRE_MINUTES",
        "30",
    )
    monkeypatch.setenv(
        "EDUNOVA_REFRESH_TOKEN_EXPIRE_DAYS",
        "14",
    )
    monkeypatch.setenv(
        "EDUNOVA_DATABASE_PATH",
        "production.db",
    )

    settings = Settings.from_environment()

    assert settings.environment == "production"
    assert settings.jwt_secret == (
        "production-super-secret-key-of-64-characters-minimum-length-ok"
    )
    assert settings.access_token_expire_minutes == 30
    assert settings.refresh_token_expire_days == 14
    assert settings.database_path == "production.db"


def test_production_rejects_default_jwt_secret(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "production")
    monkeypatch.setenv(
        "EDUNOVA_JWT_SECRET",
        DEVELOPMENT_JWT_SECRET,
    )

    with pytest.raises(ValueError, match="valeur par defaut"):
        Settings.from_environment()


def test_production_rejects_short_jwt_secret(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "production")
    monkeypatch.setenv("EDUNOVA_JWT_SECRET", "trop-court")

    with pytest.raises(ValueError, match="32 caracteres"):
        Settings.from_environment()


def test_production_rejects_wildcard_cors(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "production")
    monkeypatch.setenv(
        "EDUNOVA_JWT_SECRET",
        "production-super-secret-key-of-64-characters-minimum-length-ok",
    )
    monkeypatch.setenv("EDUNOVA_CORS_ALLOWED_ORIGINS", "*")

    with pytest.raises(ValueError, match="joker"):
        Settings.from_environment()


def test_unknown_environment_is_rejected(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "preprod")

    with pytest.raises(ValueError, match="EDUNOVA_ENVIRONMENT"):
        Settings.from_environment()


def test_documentation_is_disabled_by_default_in_production(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "production")
    monkeypatch.setenv(
        "EDUNOVA_JWT_SECRET",
        "production-super-secret-key-of-64-characters-minimum-length-ok",
    )
    monkeypatch.delenv("EDUNOVA_DOCS_ENABLED", raising=False)

    settings = Settings.from_environment()

    assert settings.docs_enabled is False
    assert settings.is_production is True


def test_rate_limit_settings_must_be_positive(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "development")
    monkeypatch.setenv("EDUNOVA_AUTH_RATE_LIMIT_ATTEMPTS", "0")

    with pytest.raises(ValueError, match="tentatives"):
        Settings.from_environment()
