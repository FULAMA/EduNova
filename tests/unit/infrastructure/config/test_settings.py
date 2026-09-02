import pytest

from src.infrastructure.config.settings import Settings


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
        "production-super-secret-key",
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
    assert settings.jwt_secret == "production-super-secret-key"
    assert settings.access_token_expire_minutes == 30
    assert settings.refresh_token_expire_days == 14
    assert settings.database_path == "production.db"
