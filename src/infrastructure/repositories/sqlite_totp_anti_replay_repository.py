from uuid import UUID

from src.identity.application.interfaces.totp_anti_replay_repository import (
    TotpAntiReplayRepository,
)
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteTotpAntiReplayRepository(TotpAntiReplayRepository):
    """SQLite-backed atomic TOTP anti-replay protection.

    Ensures each TOTP code interval can only be accepted once per user,
    enforced atomically via SQLite's conditional UPDATE with ON CONFLICT.

    Atomicity guarantee:
    - Only one concurrent request can succeed for the same interval
    - If interval <= last_accepted_interval, the UPDATE affects 0 rows
    - If interval > last_accepted_interval, the UPDATE affects 1 row
    - rowcount check determines success/failure
    """

    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def record_interval(
        self,
        user_id: UUID,
        interval_index: int,
    ) -> bool:
        """Atomically records interval if newer than last accepted.

        Uses a single INSERT ... ON CONFLICT ... UPDATE with WHERE condition for atomicity.
        The WHERE clause ensures only one transaction can succeed.
        Returns False on any database error (secure failure).
        """
        try:
            with self._database.connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO totp_anti_replay (user_id, last_accepted_interval)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO UPDATE
                    SET last_accepted_interval = ?
                    WHERE last_accepted_interval < ?
                    """,
                    (
                        str(user_id),
                        interval_index,
                        interval_index,
                        interval_index,
                    ),
                )
                return cursor.rowcount == 1
        except Exception:
            return False

    def get_last_interval(self, user_id: UUID) -> int | None:
        """Retrieves the last accepted interval for a user.
        
        Returns None on any database error (secure failure).
        """
        try:
            with self._database.connect() as connection:
                row = connection.execute(
                    """
                    SELECT last_accepted_interval
                    FROM totp_anti_replay
                    WHERE user_id = ?
                    """,
                    (str(user_id),),
                ).fetchone()

                if row is None:
                    return None

                return row["last_accepted_interval"]
        except Exception:
            return None
