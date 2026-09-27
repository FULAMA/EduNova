from uuid import uuid4

import pyotp
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

    secret = pyotp.random_base32()

    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_secret=secret,
        two_factor_enabled=False,
    )

    user_repository.save(user)

    seed_membership(
        container,
        user.id,
        tenant_id=TEST_TENANT_ID,
        role="ADMIN",
    )

    app = create_app(container)

    return TestClient(app), user, secret


def create_admin_token(
    user: User,
    tenant_id=TEST_TENANT_ID,
) -> str:
    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    return jwt_service.create_access_token(
        user_id=user.id,
        role=user.role,
        tenant_id=tenant_id,
    )


def test_verify_two_factor_http_success():
    client, user, secret = create_test_environment()

    token = create_admin_token(user)

    code = pyotp.TOTP(secret).now()

    response = client.post(
        f"/auth/2fa/verify/{user.id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "code": code,
        },
    )

    assert response.status_code == 200
    assert response.json()["verified"] is True


def test_verify_two_factor_http_invalid_code():
    client, user, _ = create_test_environment()

    token = create_admin_token(user)

    response = client.post(
        f"/auth/2fa/verify/{user.id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "code": "000000",
        },
    )

    assert response.status_code == 400


def test_verify_two_factor_http_unknown_user():
    client, user, _ = create_test_environment()

    token = create_admin_token(user)

    response = client.post(
        f"/auth/2fa/verify/{uuid4()}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "code": "123456",
        },
    )

    assert response.status_code == 404


def test_verify_two_factor_http_requires_authentication():
    client, user, secret = create_test_environment()

    code = pyotp.TOTP(secret).now()

    response = client.post(
        f"/auth/2fa/verify/{user.id}",
        json={
            "code": code,
        },
    )

    assert response.status_code == 401


def test_verify_two_factor_http_cross_tenant_is_rejected():
    client, user, secret = create_test_environment()

    other_tenant_id = uuid4()

    token = create_admin_token(
        user,
        tenant_id=other_tenant_id,
    )

    code = pyotp.TOTP(secret).now()

    response = client.post(
        f"/auth/2fa/verify/{user.id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "code": code,
        },
    )

    assert response.status_code == 403

