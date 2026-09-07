from uuid import uuid4

from fastapi.testclient import TestClient

from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.auth_helpers import authenticate_as


def test_academic_record_full_http_workflow():
    student_id = uuid4()
    academic_period_id = uuid4()
    subject_math_id = uuid4()
    subject_physics_id = uuid4()

    container = ApplicationContainer(
        database_path=":memory:"
    )

    app = create_app(container)
    authenticate_as(app)
    client = TestClient(app)

    # 1. Création du dossier académique
    response = client.post(
        "/academic-records",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(academic_period_id),
            "total_credits": 30,
        },
    )

    assert response.status_code == 201

    # 2. Ajout de Mathématiques : 16 × coefficient 3
    response = client.post(
        f"/academic-records/{student_id}/{academic_period_id}/subjects",
        json={
            "subject_id": str(subject_math_id),
            "average": 16,
            "coefficient": 3,
        },
    )

    assert response.status_code == 201

    # 3. Ajout de Physique : 12 × coefficient 2
    response = client.post(
        f"/academic-records/{student_id}/{academic_period_id}/subjects",
        json={
            "subject_id": str(subject_physics_id),
            "average": 12,
            "coefficient": 2,
        },
    )

    assert response.status_code == 201

    # 4. Consultation du dossier
    response = client.get(
        f"/academic-records/{student_id}/{academic_period_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["student_id"] == str(student_id)
    assert data["academic_period_id"] == str(academic_period_id)

    # (16 × 3 + 12 × 2) / (3 + 2) = 14.4
    assert data["general_average"] == 14.4

    assert data["failed_subjects"] == 0
    assert data["total_credits"] == 30

    assert len(data["subject_results"]) == 2

    assert data["subject_results"][0] == {
        "subject_id": str(subject_math_id),
        "average": 16,
        "coefficient": 3,
    }

    assert data["subject_results"][1] == {
        "subject_id": str(subject_physics_id),
        "average": 12,
        "coefficient": 2,
    }
