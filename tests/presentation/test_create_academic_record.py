from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.identity.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.tenant import TEST_TENANT_ID, seed_membership


JWT_SECRET = "edunova-development-secret-key-32-bytes-minimum-change-in-production"


class FakeCreateAcademicRecord:
    def __init__(self):
        self.received_request = None

    def execute(self, request):
        self.received_request = request
        raise ValueError("Academic record already exists")


def authenticated_client(app, container):
    user = User(
        id=uuid4(),
        email="create-record@edunova.com",
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


def test_create_academic_record_route_uses_injected_use_case():
    student_id = uuid4()
    academic_period_id = uuid4()

    fake_use_case = FakeCreateAcademicRecord()

    container = ApplicationContainer(database_path=":memory:")

    app = create_app(
        container,
        create_academic_record_use_case=fake_use_case,
    )

    client = authenticated_client(app, container)

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
    assert fake_use_case.received_request.tenant_id == TEST_TENANT_ID
    assert fake_use_case.received_request.student_id == student_id
    assert fake_use_case.received_request.academic_period_id == academic_period_id

