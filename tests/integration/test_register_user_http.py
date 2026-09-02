from fastapi.testclient import TestClient

from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer


def create_test_client():
    container = ApplicationContainer(
        database_path=":memory:"
    )

    app = create_app(container)

    return TestClient(app), container


def test_register_user_http_success():
    client, _ = create_test_client()

    response = client.post(
        "/auth/register",
        json={
            "email": "admin@edunova.com",
            "password": "EduNova@2026",
            "role": "ADMIN",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "admin@edunova.com"
    assert data["role"] == "ADMIN"
    assert data["is_active"] is True
    assert data["two_factor_enabled"] is False
    assert "id" in data


def test_register_user_http_duplicate_email():
    client, _ = create_test_client()

    payload = {
        "email": "admin@edunova.com",
        "password": "EduNova@2026",
        "role": "ADMIN",
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
            "email": "admin@edunova.com",
            "password": "123",
            "role": "ADMIN",
        },
    )

    assert response.status_code == 422
