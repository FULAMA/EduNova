from datetime import datetime, timezone

from src.identity.application.interfaces.refresh_token_repository import (
    RefreshTokenRepository,
)
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteRefreshTokenRepository(RefreshTokenRepository):

    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def revoke(self, jti: str) -> None:
        if not jti.strip():
            raise ValueError("Le jti ne peut pas etre vide.")

        revoked_at = datetime.now(timezone.utc).isoformat()

        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO revoked_refresh_tokens (
                    jti,
                    revoked_at
                )
                VALUES (?, ?)
                """,
                (jti, revoked_at),
            )

    def is_revoked(self, jti: str) -> bool:
        if not jti.strip():
            raise ValueError("Le jti ne peut pas etre vide.")

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM revoked_refresh_tokens
                WHERE jti = ?
                """,
                (jti,),
            ).fetchone()

        return row is not None
