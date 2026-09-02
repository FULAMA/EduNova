import pytest

from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_refresh_token_repository import (
    SQLiteRefreshTokenRepository,
)


def create_repository():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    return SQLiteRefreshTokenRepository(database)


def test_token_is_not_revoked_initially():
    repository = create_repository()

    assert repository.is_revoked("token-123") is False


def test_revoke_token():
    repository = create_repository()

    repository.revoke("token-123")

    assert repository.is_revoked("token-123") is True


def test_revoke_does_not_affect_another_token():
    repository = create_repository()

    repository.revoke("token-123")

    assert repository.is_revoked("token-456") is False


def test_revoke_same_token_twice_is_safe():
    repository = create_repository()

    repository.revoke("token-123")
    repository.revoke("token-123")

    assert repository.is_revoked("token-123") is True


def test_revoke_rejects_empty_jti():
    repository = create_repository()

    with pytest.raises(ValueError):
        repository.revoke("")


def test_is_revoked_rejects_empty_jti():
    repository = create_repository()

    with pytest.raises(ValueError):
        repository.is_revoked("")
