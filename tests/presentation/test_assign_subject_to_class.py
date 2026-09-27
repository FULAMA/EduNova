from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.academic.domain.entities.class_subject import ClassSubject
from src.identity.domain.entities.user import User
from src.presentation.api.app import create_app
from tests.support.tenant import TEST_TENANT_ID, seed_membership


JWT_SECRET = "edunova-development-secret-key-32-bytes-minimum-change-in-production"


class FakeAssignSubjectToClass:
    def __init__(self):
        self.called_with = None

    def execute(self, request):
        self.called_with = {
            "tenant_id": request.tenant_id,
            "academic_class_id": request.academic_class_id,
            "subject_id": request.subject_id,
            "coefficient": request.coefficient,
            "academic_option_id": request.academic_option_id,
        }

        return ClassSubject(
            id=uuid4(),
            tenant_id=request.tenant_id,
            academic_class_id=request.academic_class_id,
            subject_id=request.subject_id,
            coefficient=request.coefficient,
            academic_option_id=request.academic_option_id,
        )
def authenticated_client(app, application_container):
    user = User(
        id=uuid4(),
        email="assign-subject@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    application_container._user_repository().save(user)

    seed_membership(
        application_container,
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


def test_assign_subject_to_class_route_uses_injected_use_case(application_container):
    class_id = uuid4()
    subject_id = uuid4()

    fake_use_case = FakeAssignSubjectToClass()

    app = create_app(
        application_container,
        assign_subject_to_class_use_case=fake_use_case,
    )

    client = authenticated_client(app, application_container)

    response = client.post(
        f"/classes/{class_id}/subjects",
        json={
            "subject_id": str(subject_id),
            "coefficient": 4,
        },
    )

    assert response.status_code == 201
    assert fake_use_case.called_with["tenant_id"] == TEST_TENANT_ID
    assert fake_use_case.called_with["academic_class_id"] == class_id
    assert fake_use_case.called_with["subject_id"] == subject_id
    assert fake_use_case.called_with["coefficient"] == 4


def test_assign_subject_to_class_rejects_invalid_coefficient(application_container):
    app = create_app(application_container)

    client = authenticated_client(app, application_container)

    response = client.post(
        f"/classes/{uuid4()}/subjects",
        json={
            "subject_id": str(uuid4()),
            "coefficient": 0,
        },
    )

    assert response.status_code == 422


