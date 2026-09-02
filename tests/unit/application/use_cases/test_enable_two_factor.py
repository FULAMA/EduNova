from uuid import uuid4

import pytest

from src.application.use_cases.enable_two_factor import (
    EnableTwoFactor,
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

    def generate_secret(self):
        return "JBSWY3DPEHPK3PXP"

    def generate_provisioning_uri(self, email, secret):
        return (
            "otpauth://totp/EduNova:"
            + email
            + "?secret="
            + secret
        )


def test_enable_two_factor_generates_secret_and_uri():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    repository = FakeUserRepository(user)
    two_factor_service = FakeTwoFactorService()

    use_case = EnableTwoFactor(
        user_repository=repository,
        two_factor_service=two_factor_service,
    )

    result = use_case.execute(user.id)

    assert result.secret == "JBSWY3DPEHPK3PXP"
    assert result.provisioning_uri.startswith(
        "otpauth://totp/EduNova:"
    )

    assert repository.saved_user is not None
    assert repository.saved_user.two_factor_secret == (
        "JBSWY3DPEHPK3PXP"
    )

    assert repository.saved_user.two_factor_enabled is False


def test_enable_two_factor_fails_for_unknown_user():
    repository = FakeUserRepository()
    two_factor_service = FakeTwoFactorService()

    use_case = EnableTwoFactor(
        user_repository=repository,
        two_factor_service=two_factor_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(uuid4())
