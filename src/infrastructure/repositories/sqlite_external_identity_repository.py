import sqlite3
from uuid import UUID

from src.identity.application.interfaces.external_identity_repository import (
    ExternalIdentityRepository,
)
from src.identity.domain.entities.external_identity import ExternalIdentity
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteExternalIdentityRepository(ExternalIdentityRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def find_by_provider_and_subject(
        self,
        provider: str,
        subject: str,
    ) -> ExternalIdentity | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, provider, subject, user_id
                FROM external_identities
                WHERE provider = ? AND subject = ?
                """,
                (provider, subject),
            ).fetchone()
        return self._to_domain(row) if row is not None else None

    def find_by_user_and_provider(
        self,
        user_id: UUID,
        provider: str,
    ) -> ExternalIdentity | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, provider, subject, user_id
                FROM external_identities
                WHERE user_id = ? AND provider = ?
                """,
                (str(user_id), provider),
            ).fetchone()
        return self._to_domain(row) if row is not None else None

    def link(self, identity: ExternalIdentity) -> ExternalIdentity:
        try:
            with self._database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO external_identities (
                        id, provider, subject, user_id
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        str(identity.id),
                        identity.provider,
                        identity.subject,
                        str(identity.user_id),
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError("Identite Google deja liee.") from exc
        return identity

    @staticmethod
    def _to_domain(row) -> ExternalIdentity:
        return ExternalIdentity(
            id=UUID(row["id"]),
            provider=row["provider"],
            subject=row["subject"],
            user_id=UUID(row["user_id"]),
        )
