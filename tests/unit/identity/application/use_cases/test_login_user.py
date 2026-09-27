from uuid import uuid4

import pytest

from src.identity.application.dto.login_user_request import LoginUserRequest
from src.identity.application.use_cases.login_user import LoginUser
from src.identity.domain.entities.user import User
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant
from tests.support.tenant import TEST_TENANT_ID


class FakeUserRepository:

    def __init__(self, user=None):
        self.user = user

    def save(self, user):
        self.user = user

    def find_by_id(self, user_id):
        if self.user is not None and self.user.id == user_id:
            return self.user
        return None

    def find_by_email(self, email):
        if self.user is not None and self.user.email == email:
            return self.user
        return None


class FakeMembershipRepository:

    def __init__(self, membership=None):
        self.membership = membership

    def find_by_user_and_tenant(self, user_id, tenant_id):
        if self.membership is None:
            return None
        if (
            self.membership.user_id == user_id
            and self.membership.tenant_id == tenant_id
        ):
            return self.membership
        return None


class FakeTenantRepository:

    def __init__(self, tenant=None):
        self.tenant = tenant

    def find_by_id(self, tenant_id):
        if self.tenant is not None and self.tenant.id == tenant_id:
            return self.tenant
        return None


class FakePasswordHasher:

    def __init__(self, valid=True):
        self.valid = valid

    def hash(self, password):
        return "hashed-password"

    def verify(self, password, password_hash):
        return self.valid


class FakeTwoFactorService:

    def __init__(self, valid=True):
        self.valid = valid

    def verify_code(self, secret, code):
        return self.valid


class FakeJwtService:

    def create_access_token(self, user_id, role, tenant_id):
        return "access-token"

    def create_refresh_token(self, user_id, tenant_id):
        return "refresh-token"

    def create_two_factor_token(self, user_id, tenant_id):
        return "two-factor-token"


def create_tenant_environment(user):
    tenant = Tenant(
        id=TEST_TENANT_ID,
        name="EduNova Test",
        slug="edunova-test",
        active=True,
    )

    membership = Membership(
        id=uuid4(),
        user_id=user.id,
        tenant_id=TEST_TENANT_ID,
        role=user.role,
        active=True,
    )

    return FakeMembershipRepository(membership), FakeTenantRepository(tenant)


def test_login_without_2fa_returns_tokens():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=False,
    )

    membership_repository, tenant_repository = create_tenant_environment(user)

    use_case = LoginUser(
        user_repository=FakeUserRepository(user),
        membership_repository=membership_repository,
        tenant_repository=tenant_repository,
        password_hasher=FakePasswordHasher(valid=True),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    result = use_case.execute(
        LoginUserRequest(
            email="admin@edunova.com",
            password="EduNova@2026",
            tenant_id=TEST_TENANT_ID,
        )
    )
    assert result.authenticated is True
    assert result.two_factor_required is False
    assert result.two_factor_token is None
    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"


def test_login_with_2fa_returns_pending_token():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    membership_repository, tenant_repository = create_tenant_environment(user)

    use_case = LoginUser(
        user_repository=FakeUserRepository(user),
        membership_repository=membership_repository,
        tenant_repository=tenant_repository,
        password_hasher=FakePasswordHasher(valid=True),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    result = use_case.execute(
        LoginUserRequest(
            email="admin@edunova.com",
            password="EduNova@2026",
            tenant_id=TEST_TENANT_ID,
        )
    )
    assert result.authenticated is False
    assert result.two_factor_required is True
    assert result.two_factor_token == "two-factor-token"
    assert result.access_token is None
    assert result.refresh_token is None


def test_login_rejects_unknown_email():
    use_case = LoginUser(
        user_repository=FakeUserRepository(),
        membership_repository=FakeMembershipRepository(),
        tenant_repository=FakeTenantRepository(),
        password_hasher=FakePasswordHasher(),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            LoginUserRequest(
                email="unknown@edunova.com",
                password="EduNova@2026",
                tenant_id=TEST_TENANT_ID,

            )
        )


def test_login_rejects_wrong_password():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    use_case = LoginUser(
        user_repository=FakeUserRepository(user),
        membership_repository=FakeMembershipRepository(),
        tenant_repository=FakeTenantRepository(),
        password_hasher=FakePasswordHasher(valid=False),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            LoginUserRequest(
                email="admin@edunova.com",
                password="WrongPassword",
                tenant_id=TEST_TENANT_ID,

            )
        )


def test_login_rejects_inactive_user():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        is_active=False,
    )

    use_case = LoginUser(
        user_repository=FakeUserRepository(user),
        membership_repository=FakeMembershipRepository(),
        tenant_repository=FakeTenantRepository(),
        password_hasher=FakePasswordHasher(valid=True),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            LoginUserRequest(
                email="admin@edunova.com",
                password="EduNova@2026",
                tenant_id=TEST_TENANT_ID,

            )
        )


def test_login_rejects_empty_email():
    use_case = LoginUser(
        user_repository=FakeUserRepository(),
        membership_repository=FakeMembershipRepository(),
        tenant_repository=FakeTenantRepository(),
        password_hasher=FakePasswordHasher(),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError, match="L email ne peut pas etre vide"):
        use_case.execute(
            LoginUserRequest(
                email="   ",
                password="EduNova@2026",
                tenant_id=TEST_TENANT_ID,

            )
        )


def test_login_rejects_empty_password():
    use_case = LoginUser(
        user_repository=FakeUserRepository(),
        membership_repository=FakeMembershipRepository(),
        tenant_repository=FakeTenantRepository(),
        password_hasher=FakePasswordHasher(),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(
        ValueError,
        match="Le mot de passe ne peut pas etre vide",
    ):
        use_case.execute(
            LoginUserRequest(
                email="admin@edunova.com",
                password="",
                tenant_id=TEST_TENANT_ID,

            )
        )


def test_login_rejects_missing_tenant():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    use_case = LoginUser(
        user_repository=FakeUserRepository(user),
        membership_repository=FakeMembershipRepository(),
        tenant_repository=FakeTenantRepository(),
        password_hasher=FakePasswordHasher(valid=True),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError, match="Acces tenant refuse"):
        use_case.execute(
            LoginUserRequest(
                email="admin@edunova.com",
                password="EduNova@2026",
                tenant_id=TEST_TENANT_ID,

            )
        )


def test_login_rejects_inactive_tenant():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    tenant = Tenant(
        id=TEST_TENANT_ID,
        name="EduNova Test",
        slug="edunova-test",
        active=False,
    )

    membership = Membership(
        id=uuid4(),
        user_id=user.id,
        tenant_id=TEST_TENANT_ID,
        role="ADMIN",
        active=True,
    )

    use_case = LoginUser(
        user_repository=FakeUserRepository(user),
        membership_repository=FakeMembershipRepository(membership),
        tenant_repository=FakeTenantRepository(tenant),
        password_hasher=FakePasswordHasher(valid=True),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError, match="Acces tenant refuse"):
        use_case.execute(
            LoginUserRequest(
                email="admin@edunova.com",
                password="EduNova@2026",
                tenant_id=TEST_TENANT_ID,

            )
        )


def test_login_rejects_inactive_membership():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    membership = Membership(
        id=uuid4(),
        user_id=user.id,
        tenant_id=TEST_TENANT_ID,
        role="ADMIN",
        active=False,
    )

    tenant = Tenant(
        id=TEST_TENANT_ID,
        name="EduNova Test",
        slug="edunova-test",
        active=True,
    )

    use_case = LoginUser(
        user_repository=FakeUserRepository(user),
        membership_repository=FakeMembershipRepository(membership),
        tenant_repository=FakeTenantRepository(tenant),
        password_hasher=FakePasswordHasher(valid=True),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError, match="Acces tenant refuse"):
        use_case.execute(
            LoginUserRequest(
                email="admin@edunova.com",
                password="EduNova@2026",
                tenant_id=TEST_TENANT_ID,

            )
        )
