from uuid import uuid4

from fastapi.testclient import TestClient

from src.presentation.api.app import create_app


class FakeCreateAcademicRecord:
    def execute(self, request):
        raise ValueError("Academic record already exists")


def test_create_academic_record_route_uses_injected_use_case():
    student_id = uuid4()
    academic_period_id = uuid4()

    fake_use_case = FakeCreateAcademicRecord()

    app = create_app(
        create_academic_record_use_case=fake_use_case
    )

    client = TestClient(app)

    response = client.post(
        "/academic-records",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(academic_period_id),
            "total_credits": 30,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Academic record already exists"
