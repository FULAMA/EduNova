from fastapi.testclient import TestClient

from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from src.infrastructure.config.settings import Settings


def build_settings(environment: str = "test") -> Settings:
    return Settings(
        environment=environment,
        jwt_secret="test-secret-key-32-bytes-minimum",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
        database_path=":memory:",
        cors_allowed_origins=(
            "http://localhost:3000",
            "http://localhost:5173",
        ),
    )


def build_client(environment: str = "test") -> TestClient:
    settings = build_settings(environment)
    container = ApplicationContainer(settings=settings)
    return TestClient(create_app(container=container))


def test_security_headers_are_present():
    client = build_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"] == (
        "geolocation=(), microphone=(), camera=()"
    )


def test_hsts_is_not_enabled_in_test_environment():
    client = build_client()

    response = client.get("/health")

    assert "Strict-Transport-Security" not in response.headers


def test_hsts_is_enabled_in_production():
    client = build_client("production")

    response = client.get("/health")

    assert response.headers["Strict-Transport-Security"] == (
        "max-age=31536000; includeSubDomains"
    )


def test_cors_allows_configured_origin():
    client = build_client()

    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == (
        "http://localhost:3000"
    )


def test_cors_rejects_unconfigured_origin():
    client = build_client()

    response = client.get(
        "/health",
        headers={"Origin": "https://evil.example"},
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
def test_api_documentation_is_disabled_in_production():
    client = build_client("production")

    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_api_documentation_is_available_in_test():
    client = build_client()

    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert client.get("/openapi.json").status_code == 200
