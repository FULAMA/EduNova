from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.domain.entities.user import User
from src.domain.value_objects.academic_risk import RiskLevel
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
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

    def execute(
        self,
        tenant_id,
        academic_class_id,
        subject_id,
        coefficient,
        academic_option_id=None,
    ):
        if self.error is not None:
            raise ValueError(self.error)

        return type(
            "FakeResult",
            (),
            {
                "id": uuid4(),
                "academic_class_id": academic_class_id,
                "subject_id": subject_id,
                "coefficient": coefficient,
                "academic_option_id": academic_option_id,
                "active": True,
            },
        )()


def authenticated_client(app, container):
    user = User(
        id=uuid4(),
        email="hardening-admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    container._user_repository().save(user)

    seed_membership(
        container,
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


def test_analyze_academic_risk_returns_result():
    app = create_app(
        database_path=":memory:",
        analyze_academic_risk_use_case=FakeAnalyzeAcademicRisk(
            level=RiskLevel.HIGH,
            score=90,
            reasons=(
                "Moyenne générale particulièrement faible.",
                "Taux d'assiduité critique.",
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
            "Moyenne générale particulièrement faible.",
            "Taux d'assiduité critique.",
        ],
    }


def test_analyze_academic_risk_rejects_invalid_attendance_rate():
    app = create_app()
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


def test_analyze_academic_risk_rejects_negative_absences():
    app = create_app()
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


def test_assign_subject_route_maps_duplicate_to_conflict():
    class_id = uuid4()
    subject_id = uuid4()

    container = ApplicationContainer(database_path=":memory:")

    app = create_app(
        container,
        assign_subject_to_class_use_case=FakeAssignSubjectToClass(
            error="La matière est déjà assignée à cette classe",
        ),
    )

    client = authenticated_client(app, container)

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


def test_assign_subject_route_maps_missing_class_to_not_found():
    class_id = uuid4()
    subject_id = uuid4()

    container = ApplicationContainer(database_path=":memory:")

    app = create_app(
        container,
        assign_subject_to_class_use_case=FakeAssignSubjectToClass(
            error="La classe académique n'existe pas",
        ),
    )

    client = authenticated_client(app, container)

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


def test_assign_subject_route_maps_unknown_business_error_to_bad_request():
    class_id = uuid4()
    subject_id = uuid4()

    container = ApplicationContainer(database_path=":memory:")

    app = create_app(
        container,
        assign_subject_to_class_use_case=FakeAssignSubjectToClass(
            error="Erreur métier inattendue",
        ),
    )

    client = authenticated_client(app, container)

    response = client.post(
        f"/classes/{class_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "coefficient": 3,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Erreur métier inattendue"

