import pytest

from src.identity.infrastructure.security.argon2_password_hasher import (
    Argon2PasswordHasher,
)


def test_hash_password_does_not_return_plaintext():
    service = Argon2PasswordHasher()

    password = "EduNova@2026"

    hashed = service.hash(password)

    assert hashed != password


def test_hash_password_returns_argon2_hash():
    service = Argon2PasswordHasher()

    hashed = service.hash("EduNova@2026")

    assert hashed.startswith("")


def test_verify_correct_password_returns_true():
    service = Argon2PasswordHasher()

    password = "EduNova@2026"
    hashed = service.hash(password)

    assert service.verify(password, hashed) is True


def test_verify_wrong_password_returns_false():
    service = Argon2PasswordHasher()

    password = "EduNova@2026"
    hashed = service.hash(password)

    assert service.verify("WrongPassword@2026", hashed) is False


def test_same_password_produces_different_hashes():
    service = Argon2PasswordHasher()

    password = "EduNova@2026"

    first_hash = service.hash(password)
    second_hash = service.hash(password)

    assert first_hash != second_hash


def test_empty_password_is_rejected():
    service = Argon2PasswordHasher()

    with pytest.raises(ValueError):
        service.hash("")


def test_empty_hash_is_rejected():
    service = Argon2PasswordHasher()

    with pytest.raises(ValueError):
        service.verify("EduNova@2026", "")
