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
    monkeypatch.setenv(
        "EDUNOVA_CORS_ALLOWED_ORIGINS",
        "https://edunova.example.com,https://admin.edunova.example.com",
    )

    settings = Settings.from_environment()

    assert settings.environment == "production"
    assert settings.jwt_secret == "production-super-secret-key"
    assert settings.access_token_expire_minutes == 30
    assert settings.refresh_token_expire_days == 14
    assert settings.database_path == "production.db"
    assert settings.cors_allowed_origins == (
        "https://edunova.example.com",
        "https://admin.edunova.example.com",
    )

def test_development_jwt_secret_is_stable(monkeypatch):
    monkeypatch.delenv("EDUNOVA_JWT_SECRET", raising=False)
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "development")

    settings_one = Settings.from_environment()
    settings_two = Settings.from_environment()

    assert settings_one.jwt_secret == settings_two.jwt_secret

def test_development_jwt_secret_is_stable(monkeypatch):
    monkeypatch.delenv("EDUNOVA_JWT_SECRET", raising=False)
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "development")

    settings_one = Settings.from_environment()
    settings_two = Settings.from_environment()

    assert settings_one.jwt_secret == settings_two.jwt_secret


@pytest.mark.parametrize(
    "weak_secret",
    [
        "change-this-secret-in-production",
        "secret",
        "changeme",
    ],
)
def test_production_rejects_known_weak_jwt_secrets(monkeypatch, weak_secret):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "production")
    monkeypatch.setenv("EDUNOVA_JWT_SECRET", weak_secret)

    with pytest.raises(ValueError, match="valeur par defaut connue"):
        Settings.from_environment()


def test_production_rejects_jwt_secret_shorter_than_32_characters(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "production")
    monkeypatch.setenv("EDUNOVA_JWT_SECRET", "a" * 31)

    with pytest.raises(ValueError, match="32 caracteres"):
        Settings.from_environment()


def test_production_accepts_jwt_secret_with_at_least_32_characters(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "production")
    monkeypatch.setenv("EDUNOVA_JWT_SECRET", "a" * 32)
    monkeypatch.setenv("EDUNOVA_CORS_ALLOWED_ORIGINS", "https://edunova.example")

    settings = Settings.from_environment()

    assert settings.jwt_secret == "a" * 32
