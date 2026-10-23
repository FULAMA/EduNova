from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.identity.domain.entities.user import User
from src.presentation.api.container import ApplicationContainer
from src.presentation.api.app import create_app
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


class FakeAnalyzeAcademicRisk:

    def execute(self, request):
        return type(
            "FakeResult",
            (),
            {
                "level": "HIGH",
                "score": 90,
                "reasons": (
                    "Moyenne gÃ©nÃ©rale particuliÃ¨rement faible.",
                    "Taux d'assiduitÃ© critique.",
                ),
            },
        )()


def create_authenticated_app(use_case=None):
    container = ApplicationContainer(database_path=":memory:")
    user = User(
        id=uuid4(),
        email="risk@example.test",
        password_hash="hashed-password",
        role="ADMIN",
    )
    container._user_repository().save(user)
    seed_membership(container, user.id, tenant_id=TEST_TENANT_ID, role="ADMIN")

    app = create_app(
        container,
        analyze_academic_risk_use_case=use_case,
    )
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )
    return app, {"Authorization": f"Bearer {token}"}


def test_analyze_academic_risk_route_uses_injected_use_case():
    app, headers = create_authenticated_app(FakeAnalyzeAcademicRisk())
    client = TestClient(app)
    client.headers.update(headers)

    response = client.post(
        "/academic-risk",
        json={
            "average": 7,
            "attendance_rate": 50,
            "unjustified_absences": 6,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["level"] == "HIGH"
    assert body["score"] == 90
    assert len(body["reasons"]) == 2


def test_analyze_academic_risk_rejects_invalid_average():
    app, headers = create_authenticated_app()
    client = TestClient(app)
    client.headers.update(headers)

    response = client.post(
        "/academic-risk",
        json={
            "average": 25,
            "attendance_rate": 80,
            "unjustified_absences": 0,
        },
    )

    assert response.status_code == 422
