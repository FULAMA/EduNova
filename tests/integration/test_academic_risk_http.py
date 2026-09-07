from fastapi.testclient import TestClient

from src.domain.value_objects.academic_risk import RiskLevel
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.auth_helpers import authenticate_as


def create_test_client():
    container = ApplicationContainer(
        database_path=":memory:"
    )

    app = create_app(container)

    authenticate_as(app)

    return TestClient(app)


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
