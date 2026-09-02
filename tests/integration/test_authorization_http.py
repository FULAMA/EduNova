from uuid import uuid4

from fastapi.testclient import TestClient

from src.application.services.jwt_service import JwtService
from src.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer


JWT_SECRET = (
    "edunova-development-secret-key-"
    "32-bytes-minimum-change-in-production"
)


def create_test_client():
    container = ApplicationContainer(database_path=":memory:")
    app = create_app(container)
    return TestClient(app), container


def create_token(user_id, role):
    jwt_service = JwtService(secret_key=JWT_SECRET)
    return jwt_service.create_access_token(
        user_id=user_id,
        role=role,
    )


def create_user(container, role):
    user = User(
        id=uuid4(),
        email=f"{role.lower()}@edunova.com",
        password_hash="hashed-password",
        role=role,
    )
    container._user_repository().save(user)
    return user


def test_teacher_cannot_access_admin_2fa_setup():
    client, container = create_test_client()

    user = create_user(container, "TEACHER")
    token = create_token(user.id, user.role)

    response = client.post(
        f"/auth/2fa/setup/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Acces interdit."


def test_student_cannot_access_admin_2fa_setup():
    client, container = create_test_client()

    user = create_user(container, "STUDENT")
    token = create_token(user.id, user.role)

    response = client.post(
        f"/auth/2fa/setup/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Acces interdit."


def test_admin_can_access_2fa_setup():
    client, container = create_test_client()

    user = create_user(container, "ADMIN")
    token = create_token(user.id, user.role)

    response = client.post(
        f"/auth/2fa/setup/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "secret" in response.json()
    assert "provisioning_uri" in response.json()


def test_unauthenticated_user_cannot_access_admin_2fa_setup():
    client, _ = create_test_client()

    user_id = uuid4()

    response = client.post(
        f"/auth/2fa/setup/{user_id}",
    )

    assert response.status_code == 401
