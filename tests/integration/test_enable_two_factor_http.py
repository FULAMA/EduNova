from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.identity.domain.entities.user import User
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
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

    user_repository = SQLiteUserRepository(
        container._database
    )

    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    user_repository.save(user)

    seed_membership(
        container,
        user.id,
        tenant_id=TEST_TENANT_ID,
        role="ADMIN",
    )

    app = create_app(container)

    return TestClient(app), user


def create_admin_token(user: User) -> str:
    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    return jwt_service.create_access_token(
        user_id=user.id,
        role=user.role,
        tenant_id=TEST_TENANT_ID,
    )


def test_enable_two_factor_http_success():
    client, user = create_test_environment()

    token = create_admin_token(user)

    response = client.post(
        f"/auth/2fa/setup/{user.id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["secret"]
    assert data["provisioning_uri"].startswith(
        "otpauth://totp/"
    )


def test_enable_two_factor_http_unknown_user():
    client, user = create_test_environment()

    token = create_admin_token(user)

    response = client.post(
        f"/auth/2fa/setup/{uuid4()}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404

