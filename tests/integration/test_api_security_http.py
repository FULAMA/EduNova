from uuid import uuid4

from fastapi.testclient import TestClient

from src.domain.entities.user import User
from src.infrastructure.config.settings import Settings
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer


def build_settings(**overrides) -> Settings:
    defaults = dict(
        environment="test",
        jwt_secret="edunova-test-secret-key-of-32-characters",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
        database_path=":memory:",
    )

    defaults.update(overrides)

    return Settings(**defaults)


def create_test_client(**settings_overrides):
    container = ApplicationContainer(
        database_path=":memory:",
        settings=build_settings(**settings_overrides),
    )

    app = create_app(container)

    return TestClient(app), container


def create_user(container, role: str) -> User:
    user = User(
        id=uuid4(),
        email=f"{role.lower()}@edunova.com",
        password_hash="hashed-password",
        role=role,
    )

    container.user_repository().save(user)

    return user


def auth_headers(container, user: User) -> dict[str, str]:
    token = container.jwt_service().create_access_token(
        user_id=user.id,
        role=user.role,
    )

    return {"Authorization": f"Bearer {token}"}


def test_academic_record_requires_authentication():
    client, _ = create_test_client()

    response = client.get(
        f"/academic-records/{uuid4()}/{uuid4()}",
    )

    assert response.status_code == 401


def test_academic_record_rejects_student_role():
    client, container = create_test_client()

    student = create_user(container, "STUDENT")

    response = client.get(
        f"/academic-records/{uuid4()}/{uuid4()}",
        headers=auth_headers(container, student),
    )

    assert response.status_code == 403


def test_academic_risk_requires_authentication():
    client, _ = create_test_client()

    response = client.post(
        "/academic-risk",
        json={
            "average": 12,
            "attendance_rate": 90,
            "unjustified_absences": 0,
        },
    )

    assert response.status_code == 401


def test_class_subject_assignment_requires_admin():
    client, container = create_test_client()

    teacher = create_user(container, "TEACHER")

    response = client.post(
        f"/classes/{uuid4()}/subjects",
        json={
            "subject_id": str(uuid4()),
            "coefficient": 3,
        },
        headers=auth_headers(container, teacher),
    )

    assert response.status_code == 403


def test_token_is_rejected_when_role_changed():
    client, container = create_test_client()

    admin = create_user(container, "ADMIN")

    headers = auth_headers(container, admin)

    admin.role = "STUDENT"
    container.user_repository().save(admin)

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 401


def test_two_factor_verification_rejects_other_user():
    client, container = create_test_client()

    student = create_user(container, "STUDENT")
    other_user = create_user(container, "TEACHER")

    response = client.post(
        f"/auth/2fa/verify/{other_user.id}",
        json={"code": "123456"},
        headers=auth_headers(container, student),
    )

    assert response.status_code == 403


def test_login_is_rate_limited():
    client, _ = create_test_client(
        auth_rate_limit_attempts=3,
        auth_rate_limit_window_seconds=60,
    )

    payload = {
        "email": "inconnu@edunova.com",
        "password": "EduNova@2026",
    }

    for _ in range(3):
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 429
    assert response.headers["Retry-After"]


def test_security_headers_are_present():
    client, _ = create_test_client()

    response = client.get("/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cache-Control"] == "no-store"
    assert "default-src 'none'" in (
        response.headers["Content-Security-Policy"]
    )
    assert "Strict-Transport-Security" not in response.headers


def test_production_enables_hsts_and_hides_documentation():
    client, _ = create_test_client(
        environment="production",
        docs_enabled=False,
    )

    response = client.get("/health")

    assert "Strict-Transport-Security" in response.headers

    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
