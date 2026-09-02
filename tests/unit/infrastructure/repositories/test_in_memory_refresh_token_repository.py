import pytest

from src.infrastructure.repositories.in_memory_refresh_token_repository import (
    InMemoryRefreshTokenRepository,
)


def test_token_is_not_revoked_initially():
    repository = InMemoryRefreshTokenRepository()

    assert repository.is_revoked("token-123") is False


def test_revoke_token():
    repository = InMemoryRefreshTokenRepository()

    repository.revoke("token-123")

    assert repository.is_revoked("token-123") is True


def test_revoke_does_not_affect_another_token():
    repository = InMemoryRefreshTokenRepository()

    repository.revoke("token-123")

    assert repository.is_revoked("token-456") is False


def test_revoke_same_token_twice_is_safe():
    repository = InMemoryRefreshTokenRepository()

    repository.revoke("token-123")
    repository.revoke("token-123")

    assert repository.is_revoked("token-123") is True


def test_revoke_rejects_empty_jti():
    repository = InMemoryRefreshTokenRepository()

    with pytest.raises(ValueError):
        repository.revoke("")


def test_is_revoked_rejects_empty_jti():
    repository = InMemoryRefreshTokenRepository()

    with pytest.raises(ValueError):
        repository.is_revoked("")
