from uuid import uuid4

from fastapi.testclient import TestClient

from src.domain.value_objects.academic_risk import RiskLevel
from src.presentation.api.app import create_app
from tests.auth_helpers import authenticate_as


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


def test_analyze_academic_risk_returns_result():
    app = create_app(
        analyze_academic_risk_use_case=FakeAnalyzeAcademicRisk(
            level=RiskLevel.HIGH,
            score=90,
            reasons=(
                "Moyenne générale particulièrement faible.",
                "Taux d'assiduité critique.",
            ),
        )
    )

    authenticate_as(app)
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
    authenticate_as(app)
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
    authenticate_as(app)
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

    app = create_app(
        assign_subject_to_class_use_case=FakeAssignSubjectToClass(
            error="La matière est déjà assignée à cette classe"
        )
    )

    authenticate_as(app)
    client = TestClient(app)

    response = client.post(
        f"/classes/{class_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "coefficient": 3,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "La matière est déjà assignée à cette classe"
    )


def test_assign_subject_route_maps_missing_class_to_not_found():
    class_id = uuid4()
    subject_id = uuid4()

    app = create_app(
        assign_subject_to_class_use_case=FakeAssignSubjectToClass(
            error="La classe académique n'existe pas"
        )
    )

    authenticate_as(app)
    client = TestClient(app)

    response = client.post(
        f"/classes/{class_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "coefficient": 3,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "La classe académique n'existe pas"
    )


def test_assign_subject_route_maps_unknown_business_error_to_bad_request():
    class_id = uuid4()
    subject_id = uuid4()

    app = create_app(
        assign_subject_to_class_use_case=FakeAssignSubjectToClass(
            error="Erreur métier inattendue"
        )
    )

    authenticate_as(app)
    client = TestClient(app)

    response = client.post(
        f"/classes/{class_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "coefficient": 3,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Erreur métier inattendue"
