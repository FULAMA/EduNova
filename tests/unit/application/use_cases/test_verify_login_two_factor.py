from uuid import uuid4

import pytest

from src.application.use_cases.verify_login_two_factor import (
    VerifyLoginTwoFactor,
)
from src.domain.entities.user import User


class FakeUserRepository:

    def __init__(self, user=None):
        self.user = user

    def save(self, user):
        self.user = user

    def find_by_id(self, user_id):
        if self.user is not None and self.user.id == user_id:
            return self.user
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

    def create_access_token(self, user_id, role):
        self.created_access_token = "access-token"
        return self.created_access_token

    def create_refresh_token(self, user_id):
        self.created_refresh_token = "refresh-token"
        return self.created_refresh_token


def test_verify_login_two_factor_returns_real_tokens():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )

    repository = FakeUserRepository(user)

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "2fa_pending",
        }
    )

    use_case = VerifyLoginTwoFactor(
        user_repository=repository,
        two_factor_service=FakeTwoFactorService(
            valid=True
        ),
        jwt_service=jwt_service,
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

    repository = FakeUserRepository(user)

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "access",
        }
    )

    use_case = VerifyLoginTwoFactor(
        user_repository=repository,
        two_factor_service=FakeTwoFactorService(),
        jwt_service=jwt_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            two_factor_token="wrong-token",
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

    repository = FakeUserRepository(user)

    jwt_service = FakeJwtService(
        payload={
            "sub": str(user.id),
            "type": "2fa_pending",
        }
    )

    use_case = VerifyLoginTwoFactor(
        user_repository=repository,
        two_factor_service=FakeTwoFactorService(
            valid=False
        ),
        jwt_service=jwt_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            two_factor_token="pending-token",
            code="000000",
        )


def test_verify_login_two_factor_rejects_unknown_user():
    repository = FakeUserRepository()

    jwt_service = FakeJwtService(
        payload={
            "sub": str(uuid4()),
            "type": "2fa_pending",
        }
    )

    use_case = VerifyLoginTwoFactor(
        user_repository=repository,
        two_factor_service=FakeTwoFactorService(),
        jwt_service=jwt_service,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            two_factor_token="pending-token",
            code="123456",
        )
