from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.identity.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.tenant import TEST_TENANT_ID, seed_membership


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
        tenant_id=TEST_TENANT_ID,
    )


def create_user(container, role):
    user = User(
        id=uuid4(),
        email=f"{role.lower()}@edunova.com",
        password_hash="hashed-password",
        role=role,
    )
    container._user_repository().save(user)
    seed_membership(
        container,
        user.id,
        tenant_id=TEST_TENANT_ID,
        role=role,
    )
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




def test_invalid_jwt_token_is_rejected():
    client, _ = create_test_client()

    response = client.post(
        f"/auth/2fa/setup/{uuid4()}",
        headers={"Authorization": "Bearer token-invalide"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token invalide."

def test_refresh_token_cannot_be_used_as_access_token():
    client, container = create_test_client()

    user = create_user(container, "ADMIN")

    jwt_service = JwtService(secret_key=JWT_SECRET)
    refresh_token = jwt_service.create_refresh_token(
        user_id=user.id,
        tenant_id=TEST_TENANT_ID,
    )

    response = client.post(
        f"/auth/2fa/setup/{user.id}",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token d acces requis."

def test_unknown_user_token_is_rejected():
    client, _ = create_test_client()

    unknown_user_id = uuid4()
    token = create_token(unknown_user_id, "ADMIN")

    response = client.post(
        f"/auth/2fa/setup/{unknown_user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Utilisateur introuvable."

def test_inactive_user_token_is_rejected():
    client, container = create_test_client()

    user = create_user(container, "ADMIN")
    user.is_active = False
    container._user_repository().save(user)

    token = create_token(user.id, user.role)

    response = client.post(
        f"/auth/2fa/setup/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Compte desactive."

def test_inactive_membership_is_rejected():
    client, container = create_test_client()

    user = User(
        id=uuid4(),
        email="inactive-membership@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    container._user_repository().save(user)

    seed_membership(
        container,
        user.id,
        tenant_id=TEST_TENANT_ID,
        role="ADMIN",
        active=False,
    )

    token = create_token(user.id, user.role)

    response = client.post(
        f"/auth/2fa/setup/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Acces tenant refuse."

def test_inactive_tenant_is_rejected():
    client, container = create_test_client()

    user = User(
        id=uuid4(),
        email="inactive-tenant@edunova.com",
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

    with container._database.connect() as connection:
        connection.execute(
            "UPDATE tenants SET active = 0 WHERE id = ?",
            (str(TEST_TENANT_ID),),
        )

    token = create_token(user.id, user.role)

    response = client.post(
        f"/auth/2fa/setup/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Acces tenant refuse."

def test_invalid_user_id_in_jwt_is_rejected():
    client, _ = create_test_client()

    jwt_service = JwtService(secret_key=JWT_SECRET)

    token = jwt_service.create_access_token(
        user_id=uuid4(),
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )

    import jwt as pyjwt

    payload = pyjwt.decode(
        token,
        JWT_SECRET,
        algorithms=["HS256"],
    )
    payload["sub"] = "not-a-valid-uuid"

    invalid_token = pyjwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256",
    )

    response = client.post(
        f"/auth/2fa/setup/{uuid4()}",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Identifiant utilisateur invalide."

def test_invalid_tenant_id_in_jwt_is_rejected():
    client, container = create_test_client()

    user = create_user(container, "ADMIN")

    jwt_service = JwtService(secret_key=JWT_SECRET)

    token = jwt_service.create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )

    import jwt as pyjwt

    payload = pyjwt.decode(
        token,
        JWT_SECRET,
        algorithms=["HS256"],
    )
    payload["tenant_id"] = "not-a-valid-uuid"

    invalid_token = pyjwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256",
    )

    response = client.post(
        f"/auth/2fa/setup/{user.id}",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Tenant JWT invalide."

