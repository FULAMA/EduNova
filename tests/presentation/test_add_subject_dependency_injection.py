from uuid import uuid4

from fastapi.testclient import TestClient

from src.presentation.api.app import create_app
from tests.auth_helpers import authenticate_as


class FakeAddSubjectResult:
    def execute(self, request):
        return type(
            "FakeResult",
            (),
            {
                "subject_id": request.subject_id,
                "average": request.average,
                "coefficient": request.coefficient,
            },
        )()


def test_add_subject_result_route_uses_injected_use_case():
    student_id = uuid4()
    academic_period_id = uuid4()
    subject_id = uuid4()

    fake_use_case = FakeAddSubjectResult()

    app = create_app(
        add_subject_result_use_case=fake_use_case
    )

    authenticate_as(app)
    client = TestClient(app)

    response = client.post(
        f"/academic-records/{student_id}/{academic_period_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "average": 16.5,
            "coefficient": 3,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["subject_id"] == str(subject_id)
    assert body["average"] == 16.5
    assert body["coefficient"] == 3
