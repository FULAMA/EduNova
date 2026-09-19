from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.tenant import TEST_TENANT_ID, seed_membership


JWT_SECRET = "edunova-development-secret-key-32-bytes-minimum-change-in-production"


def authenticated_client(app, container):
    user = User(
        id=uuid4(),
        email="http-integration@edunova.com",
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


def test_get_academic_record_through_http():
    student_id = uuid4()
    academic_period_id = uuid4()

    container = ApplicationContainer(
        database_path=":memory:"
    )

    app = create_app(container)
    client = authenticated_client(app, container)

    response = client.get(
        f"/academic-records/{student_id}/{academic_period_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Aucun dossier academique trouve pour cet etudiant et cette periode."

