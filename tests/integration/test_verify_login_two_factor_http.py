import pyotp
from uuid import uuid4

from fastapi.testclient import TestClient

from src.application.services.jwt_service import JwtService
from src.application.services.password_hasher_service import (
    PasswordHasherService,
)
from src.domain.entities.user import User
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer


JWT_SECRET = (
    "edunova-development-secret-key-"
    "32-bytes-minimum-change-in-production"
)


def create_test_environment():
    container = ApplicationContainer(
        database_path=":memory:"
    )

    repository = SQLiteUserRepository(
        container._database
    )

    password_hasher = PasswordHasherService()

    secret = pyotp.random_base32()

    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash=password_hasher.hash(
            "EduNova@2026"
        ),
        role="ADMIN",
        is_active=True,
        two_factor_enabled=True,
        two_factor_secret=secret,
    )

    repository.save(user)

    app = create_app(container)

    client = TestClient(app)

    return client, user, secret


def test_verify_login_two_factor_http_success():
    client, user, secret = create_test_environment()

    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    pending_token = jwt_service.create_two_factor_token(
        user_id=user.id
    )

    code = pyotp.TOTP(secret).now()

    response = client.post(
        "/auth/2fa/login",
        json={
            "two_factor_token": pending_token,
            "code": code,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["authenticated"] is True
    assert data["access_token"]
    assert data["refresh_token"]


def test_verify_login_two_factor_http_rejects_invalid_code():
    client, user, _ = create_test_environment()

    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    pending_token = jwt_service.create_two_factor_token(
        user_id=user.id
    )

    response = client.post(
        "/auth/2fa/login",
        json={
            "two_factor_token": pending_token,
            "code": "000000",
        },
    )

    assert response.status_code == 400


def test_verify_login_two_factor_http_rejects_non_pending_token():
    client, user, _ = create_test_environment()

    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    access_token = jwt_service.create_access_token(
        user_id=user.id,
        role=user.role,
    )

    response = client.post(
        "/auth/2fa/login",
        json={
            "two_factor_token": access_token,
            "code": "123456",
        },
    )

    assert response.status_code == 400


def test_verify_login_two_factor_http_rejects_unknown_user():
    client, _, _ = create_test_environment()

    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    pending_token = jwt_service.create_two_factor_token(
        user_id=uuid4()
    )

    code = pyotp.random_base32()

    response = client.post(
        "/auth/2fa/login",
        json={
            "two_factor_token": pending_token,
            "code": pyotp.TOTP(code).now(),
        },
    )

    assert response.status_code == 404
