from uuid import uuid4

from fastapi.testclient import TestClient

from src.presentation.api.app import create_app


class FakeAssignSubjectToClass:

    def execute(
        self,
        academic_class_id,
        subject_id,
        coefficient,
        academic_option_id=None,
    ):
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


def test_assign_subject_to_class_route_uses_injected_use_case():
    class_id = uuid4()
    subject_id = uuid4()

    fake_use_case = FakeAssignSubjectToClass()

    app = create_app(
        assign_subject_to_class_use_case=fake_use_case,
    )

    client = TestClient(app)

    response = client.post(
        f"/classes/{class_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "coefficient": 4,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["academic_class_id"] == str(class_id)
    assert body["subject_id"] == str(subject_id)
    assert body["coefficient"] == 4
    assert body["academic_option_id"] is None
    assert body["active"] is True


def test_assign_subject_to_class_rejects_invalid_coefficient():
    class_id = uuid4()
    subject_id = uuid4()

    app = create_app()
    client = TestClient(app)

    response = client.post(
        f"/classes/{class_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "coefficient": 0,
        },
    )

    assert response.status_code == 422
