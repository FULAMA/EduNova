from datetime import datetime, timezone

from src.identity.application.interfaces.consumed_token_repository import (
    ConsumedTokenRepository,
)
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteConsumedTokenRepository(ConsumedTokenRepository):
    """SQLite-backed atomic store for consumed single-use tokens.

    Ensures anti-replay protection across multiple workers and process restarts
    via SQLite's atomic PRIMARY KEY constraint.
    """

    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def consume(self, jti: str) -> bool:
        if not jti or not jti.strip():
            raise ValueError("Le jti ne peut pas etre vide.")

        consumed_at = datetime.now(timezone.utc).isoformat()

        with self._database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO consumed_tokens (jti, consumed_at)
                VALUES (?, ?)
                """,
                (jti.strip(), consumed_at),
            )
            return cursor.rowcount == 1

    def is_consumed(self, jti: str) -> bool:
        if not jti or not jti.strip():
            raise ValueError("Le jti ne peut pas etre vide.")

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM consumed_tokens
                WHERE jti = ?
                """,
                (jti.strip(),),
            ).fetchone()

            return row is not None
