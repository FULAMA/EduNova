from uuid import uuid4

import pytest

from src.application.use_cases.login_user import LoginUser
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

    def find_by_email(self, email):
        if self.user is not None and self.user.email == email:
            return self.user
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

    def create_access_token(self, user_id, role):
        return "access-token"

    def create_refresh_token(self, user_id):
        return "refresh-token"

    def create_two_factor_token(self, user_id):
        return "two-factor-token"


def test_login_without_2fa_returns_tokens():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        two_factor_enabled=False,
    )

    use_case = LoginUser(
        user_repository=FakeUserRepository(user),
        password_hasher=FakePasswordHasher(valid=True),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    result = use_case.execute(
        email="admin@edunova.com",
        password="EduNova@2026",
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

    use_case = LoginUser(
        user_repository=FakeUserRepository(user),
        password_hasher=FakePasswordHasher(valid=True),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    result = use_case.execute(
        email="admin@edunova.com",
        password="EduNova@2026",
    )

    assert result.authenticated is False
    assert result.two_factor_required is True
    assert result.two_factor_token == "two-factor-token"
    assert result.access_token is None
    assert result.refresh_token is None


def test_login_rejects_unknown_email():
    use_case = LoginUser(
        user_repository=FakeUserRepository(),
        password_hasher=FakePasswordHasher(),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            email="unknown@edunova.com",
            password="EduNova@2026",
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
        password_hasher=FakePasswordHasher(valid=False),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            email="admin@edunova.com",
            password="WrongPassword",
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
        password_hasher=FakePasswordHasher(valid=True),
        two_factor_service=FakeTwoFactorService(),
        jwt_service=FakeJwtService(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            email="admin@edunova.com",
            password="EduNova@2026",
        )
