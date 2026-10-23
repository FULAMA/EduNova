from uuid import uuid4

import pytest

from src.identity.application.dto.google_login_request import GoogleLoginRequest
from src.identity.domain.entities.external_identity import ExternalIdentity
from src.identity.application.interfaces.google_identity_verifier import (
    GoogleIdentity,
)
from src.identity.application.use_cases.login_with_google import LoginWithGoogle
from src.identity.domain.entities.user import User
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant
from tests.support.tenant import TEST_TENANT_ID


class FakeUserRepository:
    def __init__(self, user=None):
        self.user = user

    def find_by_email(self, email):
        if self.user is not None and self.user.email == email:
            return self.user
        return None

    def find_by_id(self, user_id):
        if self.user is not None and self.user.id == user_id:
            return self.user
        return None


class FakeExternalIdentityRepository:
    def __init__(self, identity=None):
        self.identity = identity

    def find_by_provider_and_subject(self, provider, subject):
        if (
            self.identity is not None
            and self.identity.provider == provider
            and self.identity.subject == subject
        ):
            return self.identity
        return None

    def find_by_user_and_provider(self, user_id, provider):
        if (
            self.identity is not None
            and self.identity.user_id == user_id
            and self.identity.provider == provider
        ):
            return self.identity
        return None

    def link(self, identity):
        self.identity = identity
        return identity


class FakeMembershipRepository:
    def __init__(self, membership=None):
        self.membership = membership

    def find_by_user_and_tenant(self, user_id, tenant_id):
        if self.membership is not None and (
            self.membership.user_id == user_id
            and self.membership.tenant_id == tenant_id
        ):
            return self.membership
        return None


class FakeTenantRepository:
    def find_by_id(self, tenant_id):
        if tenant_id == TEST_TENANT_ID:
            return Tenant(
                id=TEST_TENANT_ID,
                name="EduNova Test",
                slug="edunova-test",
            )
        return None


class FakeGoogleVerifier:
    def __init__(self, identity):
        self.identity = identity

    def verify(self, id_token):
        return self.identity


class FakeJwtService:
    def create_access_token(self, user_id, role, tenant_id):
        return "access-token"

    def create_refresh_token(self, user_id, tenant_id):
        return "refresh-token"

    def create_two_factor_token(self, user_id, tenant_id):
        return "two-factor-token"


def build_use_case(user, identity, linked_user=None, linked=True):
    membership = Membership(
        id=uuid4(),
        user_id=user.id,
        tenant_id=TEST_TENANT_ID,
        role=user.role,
    )
    return LoginWithGoogle(
        user_repository=FakeUserRepository(user),
        membership_repository=FakeMembershipRepository(membership),
        tenant_repository=FakeTenantRepository(),
        external_identity_repository=FakeExternalIdentityRepository(
            ExternalIdentity(
                id=uuid4(),
                provider="google",
                subject=identity.subject,
                user_id=linked_user.id if linked_user is not None else user.id,
            )
            if linked
            else None
        ),
        google_identity_verifier=FakeGoogleVerifier(identity),
        jwt_service=FakeJwtService(),
    )


def make_user(two_factor_enabled=False):
    return User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="unused-password-hash",
        role="ADMIN",
        two_factor_enabled=two_factor_enabled,
    )


def make_identity(email="admin@edunova.com", verified=True):
    return GoogleIdentity(
        subject="google-subject",
        email=email,
        email_verified=verified,
    )


def test_google_login_returns_tokens_for_existing_member():
    user = make_user()
    use_case = build_use_case(user, make_identity())

    result = use_case.execute(
        GoogleLoginRequest(id_token="google-id-token", tenant_id=TEST_TENANT_ID)
    )

    assert result.authenticated is True
    assert result.two_factor_required is False
    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"


def test_google_login_preserves_edunova_two_factor_flow():
    user = make_user(two_factor_enabled=True)
    use_case = build_use_case(user, make_identity())

    result = use_case.execute(
        GoogleLoginRequest(id_token="google-id-token", tenant_id=TEST_TENANT_ID)
    )

    assert result.authenticated is False
    assert result.two_factor_required is True
    assert result.two_factor_token == "two-factor-token"
    assert result.access_token is None
    assert result.refresh_token is None


def test_google_login_rejects_unverified_email():
    user = make_user()
    use_case = build_use_case(user, make_identity(verified=False))

    with pytest.raises(ValueError, match="e-mail Google"):
        use_case.execute(
            GoogleLoginRequest(id_token="google-id-token", tenant_id=TEST_TENANT_ID)
        )


def test_google_login_rejects_unknown_account_without_provisioning():
    user = make_user()
    use_case = build_use_case(
        user,
        make_identity(email="unknown@example.com"),
        linked=False,
    )

    with pytest.raises(ValueError, match="Identifiants invalides"):
        use_case.execute(
            GoogleLoginRequest(id_token="google-id-token", tenant_id=TEST_TENANT_ID)
        )


def test_google_login_rejects_valid_but_unlinked_identity():
    user = make_user()
    repository = FakeExternalIdentityRepository()
    use_case = LoginWithGoogle(
        user_repository=FakeUserRepository(user),
        membership_repository=FakeMembershipRepository(
            Membership(uuid4(), user.id, TEST_TENANT_ID, user.role)
        ),
        tenant_repository=FakeTenantRepository(),
        external_identity_repository=repository,
        google_identity_verifier=FakeGoogleVerifier(make_identity()),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError, match="Identifiants invalides"):
        use_case.execute(
            GoogleLoginRequest(id_token="google-id-token", tenant_id=TEST_TENANT_ID)
        )


def test_google_login_rejects_missing_tenant_membership():
    user = make_user()
    use_case = build_use_case(user, make_identity())

    with pytest.raises(ValueError, match="Acces tenant refuse"):
        use_case.execute(
            GoogleLoginRequest(
                id_token="google-id-token",
                tenant_id=uuid4(),
            )
        )
