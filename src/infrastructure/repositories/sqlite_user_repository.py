from uuid import UUID

from src.identity.application.interfaces.user_repository import (
    UserRepository,
)
from src.identity.domain.entities.user import User
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteUserRepository(UserRepository):

    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, user: User) -> None:
        with self._database.connect() as connection:

            existing = connection.execute(
                """
                SELECT id
                FROM users
                WHERE id = ?
                """,
                (str(user.id),),
            ).fetchone()

            if existing is None:
                connection.execute(
                    """
                    INSERT INTO users (
                        id,
                        email,
                        password_hash,
                        role,
                        is_active,
                        two_factor_enabled,
                        two_factor_secret
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(user.id),
                        user.email,
                        user.password_hash,
                        user.role,
                        int(user.is_active),
                        int(user.two_factor_enabled),
                        user.two_factor_secret,
                    ),
                )

            else:
                connection.execute(
                    """
                    UPDATE users
                    SET
                        email = ?,
                        password_hash = ?,
                        role = ?,
                        is_active = ?,
                        two_factor_enabled = ?,
                        two_factor_secret = ?
                    WHERE id = ?
                    """,
                    (
                        user.email,
                        user.password_hash,
                        user.role,
                        int(user.is_active),
                        int(user.two_factor_enabled),
                        user.two_factor_secret,
                        str(user.id),
                    ),
                )

    def find_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    email,
                    password_hash,
                    role,
                    is_active,
                    two_factor_enabled,
                    two_factor_secret
                FROM users
                WHERE id = ?
                """,
                (str(user_id),),
            ).fetchone()

            if row is None:
                return None

            return self._to_domain(row)

    def find_by_email(
        self,
        email: str,
    ) -> User | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    email,
                    password_hash,
                    role,
                    is_active,
                    two_factor_enabled,
                    two_factor_secret
                FROM users
                WHERE email = ?
                """,
                (email,),
            ).fetchone()

            if row is None:
                return None

            return self._to_domain(row)

    @staticmethod
    def _to_domain(row) -> User:
        return User(
            id=UUID(row["id"]),
            email=row["email"],
            password_hash=row["password_hash"],
            role=row["role"],
            is_active=bool(row["is_active"]),
            two_factor_enabled=bool(
                row["two_factor_enabled"]
            ),
            two_factor_secret=row["two_factor_secret"],
        )
