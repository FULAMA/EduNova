from uuid import uuid4

from fastapi.testclient import TestClient

from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer


def test_get_academic_record_through_http():
    student_id = uuid4()
    academic_period_id = uuid4()

    container = ApplicationContainer(
        database_path=":memory:"
    )

    app = create_app(container)
    client = TestClient(app)

    response = client.get(
        f"/academic-records/{student_id}/{academic_period_id}"
    )

    assert response.status_code == 404
