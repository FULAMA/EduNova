import pytest
from uuid import uuid4

from src.domain.entities.user import User
from src.presentation.api.dependencies.auth import require_role


def test_require_role_allows_expected_role():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    dependency = require_role("ADMIN")

    assert dependency(user) == user


def test_require_role_rejects_wrong_role():
    user = User(
        id=uuid4(),
        email="teacher@edunova.com",
        password_hash="hashed-password",
        role="TEACHER",
    )

    dependency = require_role("ADMIN")

    with pytest.raises(Exception):
        dependency(user)


def test_require_role_rejects_empty_roles():
    with pytest.raises(ValueError):
        require_role()


def test_require_role_accepts_multiple_roles():
    user = User(
        id=uuid4(),
        email="teacher@edunova.com",
        password_hash="hashed-password",
        role="TEACHER",
    )

    dependency = require_role("ADMIN", "TEACHER")

    assert dependency(user) == user
