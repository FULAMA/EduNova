from datetime import datetime, timezone

from src.identity.application.interfaces.google_nonce_repository import GoogleNonceRepository
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteGoogleNonceRepository(GoogleNonceRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, nonce_hash: str, expires_at: datetime) -> None:
        with self._database.connect() as connection:
            connection.execute(
                "DELETE FROM google_auth_nonces WHERE expires_at <= ?",
                (datetime.now(timezone.utc).isoformat(),),
            )
            connection.execute(
                "INSERT INTO google_auth_nonces (nonce_hash, expires_at) VALUES (?, ?)",
                (nonce_hash, expires_at.astimezone(timezone.utc).isoformat()),
            )

    def consume(self, nonce_hash: str, now: datetime) -> bool:
        with self._database.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM google_auth_nonces WHERE nonce_hash = ? AND expires_at > ?",
                (nonce_hash, now.astimezone(timezone.utc).isoformat()),
            )
            return cursor.rowcount == 1
