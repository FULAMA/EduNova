from src.identity.application.interfaces.refresh_token_repository import (
    RefreshTokenRepository,
)


class InMemoryRefreshTokenRepository(RefreshTokenRepository):

    def __init__(self):
        self._revoked_tokens: set[str] = set()

    def revoke(self, jti: str) -> None:
        if not jti.strip():
            raise ValueError("Le jti ne peut pas etre vide.")

        self._revoked_tokens.add(jti)

    def is_revoked(self, jti: str) -> bool:
        if not jti.strip():
            raise ValueError("Le jti ne peut pas etre vide.")

        return jti in self._revoked_tokens
