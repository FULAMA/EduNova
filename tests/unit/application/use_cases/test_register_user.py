from uuid import uuid4

import pytest

from src.application.services.password_hasher_service import (
    PasswordHasherService,
)
from src.application.use_cases.register_user import (
    RegisterUser,
)
from src.domain.entities.user import User


class FakeUserRepository:

    def __init__(self):
        self.users = []
        self.saved_user = None

    def save(self, user: User) -> None:
        self.users.append(user)
        self.saved_user = user

    def find_by_id(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def find_by_email(self, email):
        for user in self.users:
            if user.email == email:
                return user
        return None


class FakePasswordHasher:

    def hash(self, password):
        return "argon2-hashed-password"


def test_register_user_creates_user_with_hashed_password():
    repository = FakeUserRepository()
    password_hasher = FakePasswordHasher()

    use_case = RegisterUser(
        user_repository=repository,
        password_hasher=password_hasher,
    )

    result = use_case.execute(
        email="admin@edunova.com",
        password="EduNova@2026",
        role="ADMIN",
    )

    assert result.email == "admin@edunova.com"
    assert result.password_hash == "argon2-hashed-password"
    assert result.role == "ADMIN"
    assert result.is_active is True
    assert result.two_factor_enabled is False
    assert result.two_factor_secret is None


def test_register_user_persists_user():
    repository = FakeUserRepository()
    password_hasher = FakePasswordHasher()

    use_case = RegisterUser(
        user_repository=repository,
        password_hasher=password_hasher,
    )

    result = use_case.execute(
        email="admin@edunova.com",
        password="EduNova@2026",
        role="ADMIN",
    )

    assert repository.saved_user is result


def test_register_user_rejects_duplicate_email():
    existing_user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="existing-hash",
        role="ADMIN",
    )

    repository = FakeUserRepository()
    repository.save(existing_user)

    password_hasher = FakePasswordHasher()

    use_case = RegisterUser(
        user_repository=repository,
        password_hasher=password_hasher,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            email="admin@edunova.com",
            password="EduNova@2026",
            role="ADMIN",
        )


def test_register_user_rejects_empty_password():
    repository = FakeUserRepository()
    password_hasher = FakePasswordHasher()

    use_case = RegisterUser(
        user_repository=repository,
        password_hasher=password_hasher,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            email="admin@edunova.com",
            password="",
            role="ADMIN",
        )
