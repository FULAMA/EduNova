from uuid import uuid4

from fastapi.testclient import TestClient

from src.application.services.password_hasher_service import (
    PasswordHasherService,
)
from src.domain.entities.user import User
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def create_test_environment(
    two_factor_enabled=False,
    is_active=True,
):
    container = ApplicationContainer(
        database_path=":memory:"
    )

    repository = SQLiteUserRepository(
        container._database
    )

    password_hasher = PasswordHasherService()

    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash=password_hasher.hash(
            "EduNova@2026"
        ),
        role="ADMIN",
        is_active=is_active,
        two_factor_enabled=two_factor_enabled,
        two_factor_secret=(
            "JBSWY3DPEHPK3PXP"
            if two_factor_enabled
            else None
        ),
    )

    repository.save(user)
    seed_membership(container, user.id)

    app = create_app(container)

    return TestClient(app), user


def test_login_without_2fa_returns_tokens():
    client, user = create_test_environment()

    response = client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "EduNova@2026",
            "tenant_id": str(TEST_TENANT_ID),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["authenticated"] is True
    assert data["two_factor_required"] is False
    assert data["two_factor_token"] is None
    assert data["access_token"]
    assert data["refresh_token"]


def test_login_with_2fa_requires_second_factor():
    client, user = create_test_environment(
        two_factor_enabled=True
    )

    response = client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "EduNova@2026",
            "tenant_id": str(TEST_TENANT_ID),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["authenticated"] is False
    assert data["two_factor_required"] is True
    assert data["two_factor_token"]
    assert data["access_token"] is None
    assert data["refresh_token"] is None


def test_login_rejects_wrong_password():
    client, user = create_test_environment()

    response = client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "WrongPassword@2026",
            "tenant_id": str(TEST_TENANT_ID),
        },
    )

    assert response.status_code == 401


def test_login_rejects_inactive_user():
    client, user = create_test_environment(
        is_active=False
    )

    response = client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "EduNova@2026",
            "tenant_id": str(TEST_TENANT_ID),
        },
    )

    assert response.status_code == 401
