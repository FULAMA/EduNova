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
        "production-super-secret-key-32chars",
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
    assert settings.jwt_secret == "production-super-secret-key-32chars"
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


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_protected_environments_require_strong_jwt_secret(monkeypatch, environment):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", environment)
    monkeypatch.delenv("EDUNOVA_JWT_SECRET", raising=False)
    monkeypatch.setenv("EDUNOVA_CORS_ALLOWED_ORIGINS", "https://edunova.example.com")

    with pytest.raises(ValueError, match="EDUNOVA_JWT_SECRET"):
        Settings.from_environment()


@pytest.mark.parametrize("environment", ["staging", "production"])
@pytest.mark.parametrize(
    "weak_secret",
    ["secret", "changeme", "change-me", "change-this-secret-in-production", "your-secret-key-here"],
)
def test_protected_environments_reject_known_weak_jwt_secrets(monkeypatch, environment, weak_secret):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", environment)
    monkeypatch.setenv("EDUNOVA_JWT_SECRET", weak_secret)
    monkeypatch.setenv("EDUNOVA_CORS_ALLOWED_ORIGINS", "https://edunova.example.com")

    with pytest.raises(ValueError, match="32 caracteres"):
        Settings.from_environment()


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_protected_environments_reject_short_jwt_secret(monkeypatch, environment):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", environment)
    monkeypatch.setenv("EDUNOVA_JWT_SECRET", "s" * 31)
    monkeypatch.setenv("EDUNOVA_CORS_ALLOWED_ORIGINS", "https://edunova.example.com")

    with pytest.raises(ValueError, match="32 caracteres"):
        Settings.from_environment()


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_protected_environments_reject_wildcard_cors(monkeypatch, environment):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", environment)
    monkeypatch.setenv("EDUNOVA_JWT_SECRET", "s" * 32)
    monkeypatch.setenv("EDUNOVA_CORS_ALLOWED_ORIGINS", "*")

    with pytest.raises(ValueError, match="CORS"):
        Settings.from_environment()


def test_unknown_environment_is_rejected(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "prod")
    monkeypatch.setenv("EDUNOVA_JWT_SECRET", "s" * 32)

    with pytest.raises(ValueError, match="EDUNOVA_ENVIRONMENT"):
        Settings.from_environment()


def test_staging_accepts_strong_jwt_secret_and_explicit_cors(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "staging")
    monkeypatch.setenv("EDUNOVA_JWT_SECRET", "s" * 32)
    monkeypatch.setenv("EDUNOVA_CORS_ALLOWED_ORIGINS", "https://staging.edunova.example.com")

    settings = Settings.from_environment()

    assert settings.environment == "staging"
    assert settings.jwt_secret == "s" * 32
