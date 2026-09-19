from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.tenant import TEST_TENANT_ID, seed_membership


JWT_SECRET = "edunova-development-secret-key-32-bytes-minimum-change-in-production"


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

    container = ApplicationContainer(
        database_path=":memory:"
    )

    user = User(
        id=uuid4(),
        email="admin@edunova.com",
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

    app = create_app(
        container,
        add_subject_result_use_case=fake_use_case,
    )

    client = TestClient(app)

    jwt_service = JwtService(secret_key=JWT_SECRET)

    token = jwt_service.create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )

    client.headers.update(
        {
            "Authorization": f"Bearer {token}",
        }
    )

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


