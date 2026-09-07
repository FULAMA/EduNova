from uuid import uuid4

from fastapi.testclient import TestClient

from src.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer


def create_test_client():
    container = ApplicationContainer(
        database_path=":memory:"
    )

    app = create_app(container)

    return TestClient(app), container


def create_admin_headers(container):
    admin = User(
        id=uuid4(),
        email="root@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    container.user_repository().save(admin)

    token = container.jwt_service().create_access_token(
        user_id=admin.id,
        role=admin.role,
    )

    return {"Authorization": f"Bearer {token}"}


def test_register_user_http_creates_student_by_default():
    client, _ = create_test_client()

    response = client.post(
        "/auth/register",
        json={
            "email": "eleve@edunova.com",
            "password": "EduNova@2026",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "eleve@edunova.com"
    assert data["role"] == "STUDENT"
    assert data["is_active"] is True
    assert data["two_factor_enabled"] is False
    assert "id" in data


def test_register_user_http_rejects_anonymous_privileged_role():
    client, _ = create_test_client()

    response = client.post(
        "/auth/register",
        json={
            "email": "admin@edunova.com",
            "password": "EduNova@2026",
            "role": "ADMIN",
        },
    )

    assert response.status_code == 401


def test_register_user_http_rejects_non_admin_privileged_role():
    client, container = create_test_client()

    teacher = User(
        id=uuid4(),
        email="prof@edunova.com",
        password_hash="hashed-password",
        role="TEACHER",
    )

    container.user_repository().save(teacher)

    token = container.jwt_service().create_access_token(
        user_id=teacher.id,
        role=teacher.role,
    )

    response = client.post(
        "/auth/register",
        json={
            "email": "admin@edunova.com",
            "password": "EduNova@2026",
            "role": "ADMIN",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_register_user_http_allows_admin_to_create_privileged_account():
    client, container = create_test_client()

    response = client.post(
        "/auth/register",
        json={
            "email": "admin@edunova.com",
            "password": "EduNova@2026",
            "role": "ADMIN",
        },
        headers=create_admin_headers(container),
    )

    assert response.status_code == 201
    assert response.json()["role"] == "ADMIN"


def test_register_user_http_rejects_unknown_role():
    client, container = create_test_client()

    response = client.post(
        "/auth/register",
        json={
            "email": "admin@edunova.com",
            "password": "EduNova@2026",
            "role": "SUPERUSER",
        },
        headers=create_admin_headers(container),
    )

    assert response.status_code == 400


def test_register_user_http_duplicate_email():
    client, _ = create_test_client()

    payload = {
        "email": "eleve@edunova.com",
        "password": "EduNova@2026",
    }

    first_response = client.post(
        "/auth/register",
        json=payload,
    )

    second_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400


def test_register_user_http_rejects_short_password():
    client, _ = create_test_client()

    response = client.post(
        "/auth/register",
        json={
            "email": "eleve@edunova.com",
            "password": "123",
        },
    )

    assert response.status_code == 422


def test_register_user_http_rejects_weak_password():
    client, _ = create_test_client()

    response = client.post(
        "/auth/register",
        json={
            "email": "eleve@edunova.com",
            "password": "motdepassefaible",
        },
    )

    assert response.status_code == 422


def test_register_user_http_rejects_invalid_email():
    client, _ = create_test_client()

    response = client.post(
        "/auth/register",
        json={
            "email": "pas-un-email",
            "password": "EduNova@2026",
        },
    )

    assert response.status_code == 422
