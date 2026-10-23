from uuid import uuid4

from fastapi.testclient import TestClient

from src.identity.application.interfaces.google_identity_verifier import GoogleIdentity
from src.identity.domain.entities.external_identity import ExternalIdentity
from src.identity.application.use_cases.link_google_identity import LinkGoogleIdentity
from src.identity.application.use_cases.login_with_google import LoginWithGoogle
from src.identity.domain.entities.user import User
from src.infrastructure.repositories.sqlite_external_identity_repository import (
    SQLiteExternalIdentityRepository,
)
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


class FakeGoogleVerifier:
    def __init__(self, identity: GoogleIdentity):
        self.identity = identity

    def verify(self, id_token: str) -> GoogleIdentity:
        return self.identity


def create_authenticated_container() -> tuple[
    ApplicationContainer,
    User,
    TestClient,
]:
    container = ApplicationContainer(database_path=":memory:")
    user = User(
        id=uuid4(),
        email=f"user-{uuid4()}@example.test",
        password_hash="hashed-password",
        role="ADMIN",
    )
    container._user_repository().save(user)
    seed_membership(container, user.id)
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )
    client = TestClient(create_app(container))
    client.headers["Authorization"] = f"Bearer {token}"
    return container, user, client


def identity(subject: str = "google-subject", email: str = "user@example.test"):
    return GoogleIdentity(
        subject=subject,
        email=email,
        email_verified=True,
    )


def test_link_then_login_uses_persisted_google_subject():
    container, user, _ = create_authenticated_container()
    verifier = FakeGoogleVerifier(identity())
    external_repository = SQLiteExternalIdentityRepository(container._database)
    link_use_case = LinkGoogleIdentity(
        user_repository=container._user_repository(),
        external_identity_repository=external_repository,
        google_identity_verifier=verifier,
    )
    login_use_case = LoginWithGoogle(
        user_repository=container._user_repository(),
        membership_repository=container._membership_repository(),
        tenant_repository=container._tenant_repository(),
        external_identity_repository=external_repository,
        google_identity_verifier=verifier,
        jwt_service=container._jwt_service(),
    )
    client = TestClient(
        create_app(
            container,
            login_with_google_use_case=login_use_case,
            link_google_identity_use_case=link_use_case,
        )
    )
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )
    client.headers["Authorization"] = f"Bearer {token}"

    linked = client.post("/auth/google/link", json={"id_token": "google-token"})

    assert linked.status_code == 200
    assert linked.json() == {"linked": True}
    stored = external_repository.find_by_provider_and_subject(
        "google",
        "google-subject",
    )
    assert stored is not None
    assert stored.user_id == user.id

    client.headers.pop("Authorization")
    logged_in = client.post(
        "/auth/google",
        json={
            "id_token": "google-token",
            "tenant_id": str(TEST_TENANT_ID),
        },
    )

    assert logged_in.status_code == 200
    assert logged_in.json()["authenticated"] is True


def test_valid_google_email_without_persisted_link_is_rejected():
    container, _, _ = create_authenticated_container()
    verifier = FakeGoogleVerifier(identity(email="different@example.test"))
    login_use_case = LoginWithGoogle(
        user_repository=container._user_repository(),
        membership_repository=container._membership_repository(),
        tenant_repository=container._tenant_repository(),
        external_identity_repository=SQLiteExternalIdentityRepository(
            container._database
        ),
        google_identity_verifier=verifier,
        jwt_service=container._jwt_service(),
    )
    client = TestClient(
        create_app(container, login_with_google_use_case=login_use_case)
    )

    response = client.post(
        "/auth/google",
        json={
            "id_token": "google-token",
            "tenant_id": str(TEST_TENANT_ID),
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentification Google refusee."
    }


def test_google_identity_cannot_be_linked_to_two_users():
    container, first_user, _ = create_authenticated_container()
    second_user = User(
        id=uuid4(),
        email=f"second-{uuid4()}@example.test",
        password_hash="hashed-password",
        role="ADMIN",
    )
    container._user_repository().save(second_user)
    seed_membership(container, second_user.id)
    repository = SQLiteExternalIdentityRepository(container._database)
    verifier = FakeGoogleVerifier(identity())
    repository.link(
        ExternalIdentity(
            id=uuid4(),
            provider="google",
            subject="google-subject",
            user_id=first_user.id,
        )
    )
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=second_user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )
    link_use_case = LinkGoogleIdentity(
        user_repository=container._user_repository(),
        external_identity_repository=repository,
        google_identity_verifier=verifier,
    )
    client = TestClient(
        create_app(
            container,
            link_google_identity_use_case=link_use_case,
        )
    )
    client.headers["Authorization"] = f"Bearer {token}"

    response = client.post("/auth/google/link", json={"id_token": "google-token"})

    assert response.status_code == 409
    assert response.json() == {"detail": "Identite Google deja liee."}
