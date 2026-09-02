from uuid import uuid4

from fastapi.testclient import TestClient

from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer


def test_full_academic_record_http_sqlite_workflow():
    student_id = uuid4()
    academic_period_id = uuid4()
    math_subject_id = uuid4()
    physics_subject_id = uuid4()

    container = ApplicationContainer(
        database_path=":memory:"
    )

    app = create_app(container)
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

    # 2. Ajout de Mathématiques
    response = client.post(
        f"/academic-records/{student_id}/{academic_period_id}/subjects",
        json={
            "subject_id": str(math_subject_id),
            "average": 16,
            "coefficient": 3,
        },
    )

    assert response.status_code == 201

    # 3. Ajout de Physique
    response = client.post(
        f"/academic-records/{student_id}/{academic_period_id}/subjects",
        json={
            "subject_id": str(physics_subject_id),
            "average": 12,
            "coefficient": 2,
        },
    )

    assert response.status_code == 201

    # 4. Lecture depuis SQLite
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
    assert data["credits_obtained"] == 0.0
    assert data["total_credits"] == 30

    assert data["subject_results"] == [
        {
            "subject_id": str(math_subject_id),
            "average": 16,
            "coefficient": 3,
        },
        {
            "subject_id": str(physics_subject_id),
            "average": 12,
            "coefficient": 2,
        },
    ]
