from uuid import uuid4

import pyotp
from fastapi.testclient import TestClient

from src.domain.entities.user import User
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer


def create_test_environment():
    container = ApplicationContainer(
        database_path=":memory:"
    )

    repository = SQLiteUserRepository(
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

    repository.save(user)

    app = create_app(container)

    client = TestClient(app)

    access_token = container.jwt_service().create_access_token(
        user_id=user.id,
        role=user.role,
    )

    client.headers["Authorization"] = f"Bearer {access_token}"

    return client, user, secret


def test_verify_two_factor_http_success():
    client, user, secret = create_test_environment()

    code = pyotp.TOTP(secret).now()

    response = client.post(
        f"/auth/2fa/verify/{user.id}",
        json={
            "code": code,
        },
    )

    assert response.status_code == 200
    assert response.json()["verified"] is True


def test_verify_two_factor_http_invalid_code():
    client, user, _ = create_test_environment()

    response = client.post(
        f"/auth/2fa/verify/{user.id}",
        json={
            "code": "000000",
        },
    )

    assert response.status_code == 400


def test_verify_two_factor_http_unknown_user():
    client, _, _ = create_test_environment()

    response = client.post(
        f"/auth/2fa/verify/{uuid4()}",
        json={
            "code": "123456",
        },
    )

    assert response.status_code == 404
