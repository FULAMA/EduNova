from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.identity.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.tenant import TEST_TENANT_ID, seed_membership


JWT_SECRET = (
    "edunova-development-secret-key-"
    "32-bytes-minimum-change-in-production"
)


def create_test_environment(is_active: bool = True):
    container = ApplicationContainer(
        database_path=":memory:"
    )

    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        is_active=is_active,
    )

    container._user_repository().save(user)
    seed_membership(container, user.id)

    app = create_app(container)

    return TestClient(app), container, user


def create_refresh_token(user, tenant_id=TEST_TENANT_ID):
    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    return jwt_service.create_refresh_token(
        user_id=user.id, tenant_id=tenant_id
    )


def create_access_token(user, tenant_id=TEST_TENANT_ID):
    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    return jwt_service.create_access_token(
        user_id=user.id,
        role=user.role,
        tenant_id=tenant_id,
    )


def test_refresh_returns_new_tokens():
    client, _, user = create_test_environment()

    refresh_token = create_refresh_token(user)

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["authenticated"] is True
    assert data["two_factor_required"] is False
    assert data["two_factor_token"] is None
    assert data["access_token"]
    assert data["refresh_token"]

    assert data["refresh_token"] != refresh_token


def test_refresh_revokes_old_refresh_token():
    client, _, user = create_test_environment()

    refresh_token = create_refresh_token(user)

    first_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert second_response.status_code == 401


def test_refresh_rejects_invalid_token():
    client, _, _ = create_test_environment()

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "token-invalide",
        },
    )

    assert response.status_code == 401


def test_refresh_rejects_access_token():
    client, _, user = create_test_environment()

    access_token = create_access_token(user)

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": access_token,
        },
    )

    assert response.status_code == 401


def test_refresh_rejects_unknown_user():
    client, _, _ = create_test_environment()

    fake_user = User(
        id=uuid4(),
        email="unknown@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    refresh_token = create_refresh_token(fake_user)

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 401


def test_refresh_rejects_inactive_user():
    client, _, user = create_test_environment(
        is_active=False
    )

    refresh_token = create_refresh_token(user)

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 401


def test_refresh_requires_refresh_token():
    client, _, _ = create_test_environment()

    response = client.post(
        "/auth/refresh",
        json={},
    )

    assert response.status_code == 422

