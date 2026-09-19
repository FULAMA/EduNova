from uuid import uuid4

import pytest

from src.application.use_cases.verify_login_two_factor import (
    VerifyLoginTwoFactor,
)
from src.domain.entities.membership import Membership
from src.domain.entities.tenant import Tenant
from src.domain.entities.user import User
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


class FakeTwoFactorService:

    def __init__(self, valid=True):
        self.valid = valid

    def verify_code(self, secret, code):
        return self.valid


class FakeJwtService:

    def __init__(self, payload=None):
        self.payload = payload or {}
        self.created_access_token = None
        self.created_refresh_token = None

    def decode_token(self, token):
        return self.payload

    def create_access_token(self, user_id, role, tenant_id):
        self.created_access_token = "access-token"
        return self.created_access_token

    def create_refresh_token(self, user_id, tenant_id):
        self.created_refresh_token = "refresh-token"
        return self.created_refresh_token


def create_environment(
    user,
    jwt_service,
    two_factor_service,
    *,
    tenant=None,
    membership=None,
):
    if tenant is None:
        tenant = Tenant(
            id=TEST_TENANT_ID,
            name="EduNova Test",
            slug="edunova-test",
            active=True,
        )

    if membership is None:
        membership = Membership(
            id=uuid4(),
            user_id=user.id,
            tenant_id=TEST_TENANT_ID,
            role=user.role,
            active=True,
        )

    use_case = VerifyLoginTwoFactor(
        user_repository=FakeUserRepository(user),
        membership_repository=FakeMembershipRepository(membership),
        tenant_repository=FakeTenantRepository(tenant),
        two_factor_service=two_factor_service,
        jwt_service=jwt_service,
    )

    return use_case


def test_verify_login_two_factor_returns_real_tokens():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "2fa_pending",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = create_environment(
        user,
        jwt_service,
        FakeTwoFactorService(valid=True),
    )

    result = use_case.execute(
        two_factor_token="pending-token",
        code="123456",
    )

    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"


def test_verify_login_two_factor_rejects_invalid_pending_token():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "access",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = create_environment(
        user,
        jwt_service,
        FakeTwoFactorService(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            two_factor_token="wrong-token",
            code="123456",
        )


def test_verify_login_two_factor_rejects_missing_user_or_tenant():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    jwt_service = FakeJwtService(
        payload={
            "type": "2fa_pending",
        }
    )

    use_case = create_environment(
        user,
        jwt_service,
        FakeTwoFactorService(),
    )

    with pytest.raises(ValueError, match="ne contient pas d utilisateur"):
        use_case.execute(
            two_factor_token="pending-token",
            code="123456",
        )


def test_verify_login_two_factor_rejects_invalid_uuid():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    jwt_service = FakeJwtService(
        payload={
            "sub": "not-a-uuid",
            "type": "2fa_pending",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = create_environment(
        user,
        jwt_service,
        FakeTwoFactorService(),
    )

    with pytest.raises(ValueError, match="identifiant utilisateur est invalide"):
        use_case.execute(
            two_factor_token="pending-token",
            code="123456",
        )


def test_verify_login_two_factor_rejects_inactive_user():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        is_active=False,
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "2fa_pending",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = create_environment(
        user,
        jwt_service,
        FakeTwoFactorService(),
    )

    with pytest.raises(ValueError, match="compte est desactive"):
        use_case.execute(
            two_factor_token="pending-token",
            code="123456",
        )


def test_verify_login_two_factor_rejects_missing_membership():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "2fa_pending",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = VerifyLoginTwoFactor(
        user_repository=FakeUserRepository(user),
        membership_repository=FakeMembershipRepository(),
        tenant_repository=FakeTenantRepository(
            Tenant(
                id=TEST_TENANT_ID,
                name="EduNova Test",
                slug="edunova-test",
                active=True,
            )
        ),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=jwt_service,
    )

    with pytest.raises(ValueError, match="Acces tenant refuse"):
        use_case.execute(
            two_factor_token="pending-token",
            code="123456",
        )


def test_verify_login_two_factor_rejects_inactive_membership():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    membership = Membership(
        id=uuid4(),
        user_id=user.id,
        tenant_id=TEST_TENANT_ID,
        role="ADMIN",
        active=False,
    )

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "2fa_pending",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = create_environment(
        user,
        jwt_service,
        FakeTwoFactorService(),
        membership=membership,
    )

    with pytest.raises(ValueError, match="Acces tenant refuse"):
        use_case.execute(
            two_factor_token="pending-token",
            code="123456",
        )


def test_verify_login_two_factor_rejects_inactive_tenant():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    tenant = Tenant(
        id=TEST_TENANT_ID,
        name="EduNova Test",
        slug="edunova-test",
        active=False,
    )

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "2fa_pending",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = create_environment(
        user,
        jwt_service,
        FakeTwoFactorService(),
        tenant=tenant,
    )

    with pytest.raises(ValueError, match="Acces tenant refuse"):
        use_case.execute(
            two_factor_token="pending-token",
            code="123456",
        )


def test_verify_login_two_factor_rejects_disabled_two_factor():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=False,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "2fa_pending",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = create_environment(
        user,
        jwt_service,
        FakeTwoFactorService(),
    )

    with pytest.raises(ValueError, match="2FA n est pas active"):
        use_case.execute(
            two_factor_token="pending-token",
            code="123456",
        )


def test_verify_login_two_factor_rejects_missing_two_factor_secret():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret=None,
    )

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "2fa_pending",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = create_environment(
        user,
        jwt_service,
        FakeTwoFactorService(),
    )

    with pytest.raises(ValueError, match="secret 2FA est absent"):
        use_case.execute(
            two_factor_token="pending-token",
            code="123456",
        )


def test_verify_login_two_factor_rejects_invalid_code():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "2fa_pending",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = create_environment(
        user,
        jwt_service,
        FakeTwoFactorService(valid=False),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            two_factor_token="pending-token",
            code="000000",
        )


def test_verify_login_two_factor_rejects_unknown_user():
    unknown_user_id = uuid4()

    jwt_service = FakeJwtService(
        payload={
            "sub": str(unknown_user_id),
            "type": "2fa_pending",
            "tenant_id": str(TEST_TENANT_ID),
        }
    )

    use_case = VerifyLoginTwoFactor(
        user_repository=FakeUserRepository(),
        membership_repository=FakeMembershipRepository(),
        tenant_repository=FakeTenantRepository(
            Tenant(
                id=TEST_TENANT_ID,
                name="EduNova Test",
                slug="edunova-test",
                active=True,
            )
        ),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=jwt_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            two_factor_token="pending-token",
            code="123456",
        )
