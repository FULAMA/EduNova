from uuid import uuid4

from fastapi.testclient import TestClient

from src.academic.domain.value_objects.academic_risk import RiskLevel
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from src.identity.domain.entities.user import User
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def create_test_client():
    container = ApplicationContainer(
        database_path=":memory:"
    )

    user = User(
        id=uuid4(),
        email="risk-admin@example.test",
        password_hash="hashed-password",
        role="ADMIN",
    )
    container._user_repository().save(user)
    seed_membership(container, user.id, tenant_id=TEST_TENANT_ID, role="ADMIN")

    app = create_app(container)
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )
    client = TestClient(app)
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


def test_analyze_academic_risk_requires_authentication():
    app = create_app(ApplicationContainer(database_path=":memory:"))
    client = TestClient(app)

    response = client.post(
        "/academic-risk",
        json={
            "average": 14,
            "attendance_rate": 95,
            "unjustified_absences": 0,
        },
    )

    assert response.status_code == 401


def test_analyze_academic_risk_low():
    client = create_test_client()

    response = client.post(
        "/academic-risk",
        json={
            "average": 14,
            "attendance_rate": 95,
            "unjustified_absences": 0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["level"] == RiskLevel.LOW.value
    assert data["score"] == 0
    assert len(data["reasons"]) == 1


def test_analyze_academic_risk_medium():
    client = create_test_client()

    response = client.post(
        "/academic-risk",
        json={
            "average": 9,
            "attendance_rate": 75,
            "unjustified_absences": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["level"] == RiskLevel.MEDIUM.value
    assert data["score"] == 60
    assert len(data["reasons"]) == 2


def test_analyze_academic_risk_high():
    client = create_test_client()

    response = client.post(
        "/academic-risk",
        json={
            "average": 7,
            "attendance_rate": 50,
            "unjustified_absences": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["level"] == RiskLevel.HIGH.value
    assert data["score"] == 100
    assert len(data["reasons"]) == 5


def test_analyze_academic_risk_rejects_invalid_average():
    client = create_test_client()

    response = client.post(
        "/academic-risk",
        json={
            "average": 21,
            "attendance_rate": 95,
            "unjustified_absences": 0,
        },
    )

    assert response.status_code == 422


def test_analyze_academic_risk_rejects_non_finite_values():
    client = create_test_client()

    response = client.post(
        "/academic-risk",
        json={"average": "Infinity", "attendance_rate": 95, "unjustified_absences": 0},
    )

    assert response.status_code == 422
