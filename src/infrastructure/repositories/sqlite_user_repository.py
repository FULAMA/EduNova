import sqlite3
from uuid import UUID

from src.identity.application.interfaces.user_repository import (
    UserRepository,
)
from src.identity.domain.entities.user import User
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteUserRepository(UserRepository):

    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(
        self,
        user: User,
        connection: sqlite3.Connection | None = None,
    ) -> None:
        def _execute(conn: sqlite3.Connection) -> None:
            existing = conn.execute(
                """
                SELECT id
                FROM users
                WHERE id = ?
                """,
                (str(user.id),),
            ).fetchone()

            if existing is None:
                conn.execute(
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
                conn.execute(
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

        if connection is not None:
            _execute(connection)
            return

        with self._database.connect() as conn:
            _execute(conn)

    def find_by_id(
        self,
        user_id: UUID,
        connection: sqlite3.Connection | None = None,
    ) -> User | None:
        query = (
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
            """
        )
        params = (str(user_id),)

        if connection is not None:
            row = connection.execute(query, params).fetchone()
        else:
            with self._database.connect() as conn:
                row = conn.execute(query, params).fetchone()

        if row is None:
            return None

        return self._to_domain(row)

    def find_by_email(
        self,
        email: str,
        connection: sqlite3.Connection | None = None,
    ) -> User | None:
        query = (
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
            """
        )
        params = (email,)

        if connection is not None:
            row = connection.execute(query, params).fetchone()
        else:
            with self._database.connect() as conn:
                row = conn.execute(query, params).fetchone()

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
