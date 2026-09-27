from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.identity.domain.entities.user import User
from src.academic.domain.value_objects.academic_risk import RiskLevel
from src.presentation.api.app import create_app
from tests.support.tenant import TEST_TENANT_ID, seed_membership


JWT_SECRET = "edunova-development-secret-key-32-bytes-minimum-change-in-production"


class FakeAnalyzeAcademicRisk:

    def __init__(self, level=RiskLevel.HIGH, score=90, reasons=()):
        self.level = level
        self.score = score
        self.reasons = reasons

    def execute(self, request):
        return type(
            "FakeResult",
            (),
            {
                "level": self.level,
                "score": self.score,
                "reasons": self.reasons,
            },
        )()


class FakeAssignSubjectToClass:

    def __init__(self, error=None):
        self.error = error

    def execute(self, request):
        if self.error is not None:
            raise ValueError(self.error)

        return type(
            "FakeResult",
            (),
            {
                "id": uuid4(),
                "academic_class_id": request.academic_class_id,
                "subject_id": request.subject_id,
                "coefficient": request.coefficient,
                "academic_option_id": request.academic_option_id,
                "active": True,
            },
        )()
def authenticated_client(app, application_container):
    user = User(
        id=uuid4(),
        email="hardening-admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    application_container._user_repository().save(user)

    seed_membership(
        application_container,
        user.id,
        tenant_id=TEST_TENANT_ID,
        role="ADMIN",
    )

    jwt_service = JwtService(secret_key=JWT_SECRET)

    token = jwt_service.create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )

    client = TestClient(app)
    client.headers.update(
        {"Authorization": f"Bearer {token}"}
    )

    return client


def test_analyze_academic_risk_returns_result(application_container):
    app = create_app(
        application_container,
        analyze_academic_risk_use_case=FakeAnalyzeAcademicRisk(
            level=RiskLevel.HIGH,
            score=90,
            reasons=(
                "Moyenne gÃ©nÃ©rale particuliÃ¨rement faible.",
                "Taux d'assiduitÃ© critique.",
            ),
        ),
    )

    client = TestClient(app)

    response = client.post(
        "/academic-risk",
        json={
            "average": 7,
            "attendance_rate": 50,
            "unjustified_absences": 6,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "level": "HIGH",
        "score": 90,
        "reasons": [
            "Moyenne gÃ©nÃ©rale particuliÃ¨rement faible.",
            "Taux d'assiduitÃ© critique.",
        ],
    }


def test_analyze_academic_risk_rejects_invalid_attendance_rate(application_container):
    app = create_app(application_container)
    client = TestClient(app)

    response = client.post(
        "/academic-risk",
        json={
            "average": 15,
            "attendance_rate": 101,
            "unjustified_absences": 0,
        },
    )

    assert response.status_code == 422


def test_analyze_academic_risk_rejects_negative_absences(application_container):
    app = create_app(application_container)
    client = TestClient(app)

    response = client.post(
        "/academic-risk",
        json={
            "average": 15,
            "attendance_rate": 90,
            "unjustified_absences": -1,
        },
    )

    assert response.status_code == 422


def test_assign_subject_route_maps_duplicate_to_conflict(application_container):
    class_id = uuid4()
    subject_id = uuid4()

    app = create_app(
        application_container,
        assign_subject_to_class_use_case=FakeAssignSubjectToClass(
            error="La matière est déjà assignée à cette classe",
        ),
    )

    client = authenticated_client(app, application_container)

    response = client.post(
        f"/classes/{class_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "coefficient": 3,
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "La matière est déjà assignée à cette classe"
    )


def test_assign_subject_route_maps_missing_class_to_not_found(application_container):
    class_id = uuid4()
    subject_id = uuid4()

    app = create_app(
        application_container,
        assign_subject_to_class_use_case=FakeAssignSubjectToClass(
            error="La classe académique n'existe pas",
        ),
    )

    client = authenticated_client(app, application_container)

    response = client.post(
        f"/classes/{class_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "coefficient": 3,
        },
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "La classe académique n'existe pas"
    )


def test_assign_subject_route_maps_unknown_business_error_to_bad_request(application_container):
    class_id = uuid4()
    subject_id = uuid4()

    app = create_app(
        application_container,
        assign_subject_to_class_use_case=FakeAssignSubjectToClass(
            error="Erreur métier inattendue",
        ),
    )

    client = authenticated_client(app, application_container)

    response = client.post(
        f"/classes/{class_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "coefficient": 3,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Erreur métier inattendue"






