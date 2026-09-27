from uuid import uuid4

import pytest

from src.identity.application.use_cases.verify_two_factor import (
    VerifyTwoFactor,
)
from src.identity.domain.entities.user import User


class FakeUserRepository:

    def __init__(self, user=None):
        self.user = user
        self.saved_user = None

    def find_by_id(self, user_id):
        if self.user is not None and self.user.id == user_id:
            return self.user
        return None

    def save(self, user):
        self.saved_user = user


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


class FakeTwoFactorService:

    def __init__(self, valid=True):
        self.valid = valid

    def verify_code(self, secret, code):
        return self.valid


def make_membership(user_id, tenant_id, active=True):
    class Membership:
        pass

    membership = Membership()
    membership.user_id = user_id
    membership.tenant_id = tenant_id
    membership.active = active

    return membership


def test_verify_two_factor_enables_user():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_secret="JBSWY3DPEHPK3PXP",
        two_factor_enabled=False,
    )

    tenant_id = uuid4()

    repository = FakeUserRepository(user)
    membership_repository = FakeMembershipRepository(
        make_membership(user.id, tenant_id)
    )
    two_factor_service = FakeTwoFactorService(valid=True)

    use_case = VerifyTwoFactor(
        user_repository=repository,
        membership_repository=membership_repository,
        two_factor_service=two_factor_service,
    )

    result = use_case.execute(
        user_id=user.id,
        tenant_id=tenant_id,
        code="123456",
    )

    assert result is True
    assert repository.saved_user is not None
    assert repository.saved_user.two_factor_enabled is True


def test_verify_two_factor_rejects_invalid_code():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_secret="JBSWY3DPEHPK3PXP",
        two_factor_enabled=False,
    )

    tenant_id = uuid4()

    repository = FakeUserRepository(user)
    membership_repository = FakeMembershipRepository(
        make_membership(user.id, tenant_id)
    )
    two_factor_service = FakeTwoFactorService(valid=False)

    use_case = VerifyTwoFactor(
        user_repository=repository,
        membership_repository=membership_repository,
        two_factor_service=two_factor_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            user_id=user.id,
            tenant_id=tenant_id,
            code="000000",
        )


def test_verify_two_factor_fails_for_unknown_user():
    repository = FakeUserRepository()
    membership_repository = FakeMembershipRepository()
    two_factor_service = FakeTwoFactorService()

    use_case = VerifyTwoFactor(
        user_repository=repository,
        membership_repository=membership_repository,
        two_factor_service=two_factor_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            user_id=uuid4(),
            tenant_id=uuid4(),
            code="123456",
        )


def test_verify_two_factor_fails_without_configured_secret():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    tenant_id = uuid4()

    repository = FakeUserRepository(user)
    membership_repository = FakeMembershipRepository(
        make_membership(user.id, tenant_id)
    )
    two_factor_service = FakeTwoFactorService()

    use_case = VerifyTwoFactor(
        user_repository=repository,
        membership_repository=membership_repository,
        two_factor_service=two_factor_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            user_id=user.id,
            tenant_id=tenant_id,
            code="123456",
        )


def test_verify_two_factor_rejects_user_from_another_tenant():
    user = User(
        id=uuid4(),
        email="user@tenant-b.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_secret="JBSWY3DPEHPK3PXP",
        two_factor_enabled=False,
    )

    tenant_a = uuid4()
    tenant_b = uuid4()

    repository = FakeUserRepository(user)

    membership_repository = FakeMembershipRepository(
        make_membership(user.id, tenant_b)
    )

    two_factor_service = FakeTwoFactorService(valid=True)

    use_case = VerifyTwoFactor(
        user_repository=repository,
        membership_repository=membership_repository,
        two_factor_service=two_factor_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            user_id=user.id,
            tenant_id=tenant_a,
            code="123456",
        )

    assert repository.saved_user is None
