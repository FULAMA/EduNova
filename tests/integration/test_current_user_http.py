from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pyotp import random_base32

from src.application.services.jwt_service import JwtService
from src.application.services.password_hasher_service import (
    PasswordHasherService,
)
from src.domain.entities.user import User
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.presentation.api.dependencies.auth import get_current_user
from src.presentation.api.container import ApplicationContainer


JWT_SECRET = (
    "edunova-development-secret-key-"
    "32-bytes-minimum-change-in-production"
)


def create_test_environment(is_active: bool = True):
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
    )

    repository.save(user)

    app = FastAPI()

    app.dependency_overrides[
        lambda: container
    ] = lambda: container

    from src.presentation.api.dependencies.auth import (
        get_application_container,
    )

    app.dependency_overrides[
        get_application_container
    ] = lambda: container

    @app.get("/protected")
    def protected_route(
        current_user: User = Depends(get_current_user),
    ):
        return {
            "email": current_user.email,
            "role": current_user.role,
        }

    return TestClient(app), user


def test_current_user_accepts_valid_access_token():
    client, user = create_test_environment()

    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    token = jwt_service.create_access_token(
        user_id=user.id,
        role=user.role,
    )

    response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == user.email
    assert data["role"] == user.role


def test_current_user_rejects_missing_authorization():
    client, _ = create_test_environment()

    response = client.get("/protected")

    assert response.status_code == 401


def test_current_user_rejects_invalid_token():
    client, _ = create_test_environment()

    response = client.get(
        "/protected",
        headers={
            "Authorization": "Bearer token-invalide"
        },
    )

    assert response.status_code == 401


def test_current_user_rejects_refresh_token():
    client, user = create_test_environment()

    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    token = jwt_service.create_refresh_token(
        user_id=user.id
    )

    response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401


def test_current_user_rejects_two_factor_pending_token():
    client, user = create_test_environment()

    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    token = jwt_service.create_two_factor_token(
        user_id=user.id
    )

    response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401


def test_current_user_rejects_unknown_user():
    client, _ = create_test_environment()

    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    token = jwt_service.create_access_token(
        user_id=uuid4(),
        role="ADMIN",
    )

    response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401


def test_current_user_rejects_inactive_user():
    client, user = create_test_environment(
        is_active=False
    )

    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    token = jwt_service.create_access_token(
        user_id=user.id,
        role=user.role,
    )

    response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401
