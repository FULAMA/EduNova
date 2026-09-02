from uuid import uuid4

import pytest

from src.domain.entities.user import User


def test_user_is_created_with_2fa_disabled_by_default():
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    assert user.email == "admin@edunova.com"
    assert user.password_hash == "hashed-password"
    assert user.role == "ADMIN"
    assert user.is_active is True
    assert user.two_factor_enabled is False
    assert user.two_factor_secret is None


def test_user_requires_non_empty_email():
    with pytest.raises(ValueError):
        User(
            id=uuid4(),
            email="",
            password_hash="hashed-password",
            role="ADMIN",
        )


def test_user_requires_non_empty_password_hash():
    with pytest.raises(ValueError):
        User(
            id=uuid4(),
            email="admin@edunova.com",
            password_hash="",
            role="ADMIN",
        )


def test_user_requires_non_empty_role():
    with pytest.raises(ValueError):
        User(
            id=uuid4(),
            email="admin@edunova.com",
            password_hash="hashed-password",
            role="",
        )
