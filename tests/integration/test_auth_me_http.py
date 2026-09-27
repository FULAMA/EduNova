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


def create_test_environment():
    container = ApplicationContainer(
        database_path=":memory:"
    )

    app = create_app(container)

    return TestClient(app), container


def create_user(container, role="ADMIN", is_active=True):
    user = User(
        id=uuid4(),
        email=f"{role.lower()}@edunova.com",
        password_hash="hashed-password",
        role=role,
        is_active=is_active,
    )

    container._user_repository().save(user)
    seed_membership(container, user.id, role=role)

    return user


def create_access_token(user, tenant_id=TEST_TENANT_ID):
    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    return jwt_service.create_access_token(
        user_id=user.id,
        role=user.role,
        tenant_id=tenant_id,
    )


def test_get_me_returns_current_user():
    client, container = create_test_environment()

    user = create_user(container)
    token = create_access_token(user)

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(user.id)
    assert data["email"] == user.email
    assert data["role"] == user.role
    assert data["is_active"] is True
    assert data["two_factor_enabled"] is False


def test_get_me_rejects_unauthenticated_user():
    client, _ = create_test_environment()

    response = client.get("/auth/me")

    assert response.status_code == 401


def test_get_me_rejects_unknown_user():
    client, _ = create_test_environment()

    fake_user = User(
        id=uuid4(),
        email="fake@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    token = create_access_token(fake_user)

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401


def test_get_me_rejects_inactive_user():
    client, container = create_test_environment()

    user = create_user(
        container,
        is_active=False,
    )

    token = create_access_token(user)

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401

