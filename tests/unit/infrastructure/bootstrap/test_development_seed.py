import pytest

from src.infrastructure.bootstrap.development_seed import (
    DEVELOPMENT_TENANT_ID,
    DEVELOPMENT_USER_EMAIL,
)
from src.infrastructure.config.settings import Settings
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.presentation.api.container import ApplicationContainer


def test_development_seed_creates_reusable_account_and_membership():
    settings = Settings(
        environment="development",
        jwt_secret="test-secret-key-32-bytes-minimum",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
        database_path=":memory:",
        cors_allowed_origins=("http://localhost:5173",),
        development_seed_enabled=True,
        development_seed_password="DevPassword@2026",
    )

    container = ApplicationContainer(settings=settings)
    user = SQLiteUserRepository(container._database).find_by_email(
        DEVELOPMENT_USER_EMAIL
    )

    assert user is not None
    assert user.id is not None
    assert container._tenant_repository().find_by_id(DEVELOPMENT_TENANT_ID)
    assert container._membership_repository().find_by_user_and_tenant(
        user.id,
        DEVELOPMENT_TENANT_ID,
    )


def test_development_seed_is_rejected_in_production(monkeypatch):
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "production")
    monkeypatch.setenv("EDUNOVA_DEV_SEED", "true")
    monkeypatch.setenv("EDUNOVA_DEV_SEED_PASSWORD", "DevPassword@2026")
    monkeypatch.setenv("EDUNOVA_JWT_SECRET", "production-secret-key-32-bytes")
    monkeypatch.setenv(
        "EDUNOVA_CORS_ALLOWED_ORIGINS",
        "https://app.example.com",
    )

    with pytest.raises(ValueError, match="reserve aux environnements"):
        Settings.from_environment()
