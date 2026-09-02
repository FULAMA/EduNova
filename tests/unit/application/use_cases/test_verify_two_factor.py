from uuid import uuid4

import pytest

from src.application.use_cases.verify_two_factor import (
    VerifyTwoFactor,
)
from src.domain.entities.user import User


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


class FakeTwoFactorService:

    def __init__(self, valid=True):
        self.valid = valid

    def verify_code(self, secret, code):
        return self.valid


def test_verify_two_factor_enables_user():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_secret="JBSWY3DPEHPK3PXP",
        two_factor_enabled=False,
    )

    repository = FakeUserRepository(user)
    two_factor_service = FakeTwoFactorService(valid=True)

    use_case = VerifyTwoFactor(
        user_repository=repository,
        two_factor_service=two_factor_service,
    )

    result = use_case.execute(
        user_id=user.id,
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

    repository = FakeUserRepository(user)
    two_factor_service = FakeTwoFactorService(valid=False)

    use_case = VerifyTwoFactor(
        user_repository=repository,
        two_factor_service=two_factor_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            user_id=user.id,
            code="000000",
        )


def test_verify_two_factor_fails_for_unknown_user():
    repository = FakeUserRepository()
    two_factor_service = FakeTwoFactorService()

    use_case = VerifyTwoFactor(
        user_repository=repository,
        two_factor_service=two_factor_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            user_id=uuid4(),
            code="123456",
        )


def test_verify_two_factor_fails_without_configured_secret():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    repository = FakeUserRepository(user)
    two_factor_service = FakeTwoFactorService()

    use_case = VerifyTwoFactor(
        user_repository=repository,
        two_factor_service=two_factor_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            user_id=user.id,
            code="123456",
        )
