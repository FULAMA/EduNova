import sqlite3
from uuid import UUID

from src.infrastructure.persistence.database import SQLiteDatabase
from src.tenancy.application.interfaces.membership_repository import MembershipRepository
from src.tenancy.domain.entities.membership import Membership


class SQLiteMembershipRepository(MembershipRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(
        self,
        membership: Membership,
        connection: sqlite3.Connection | None = None,
    ) -> None:
        query = (
            "INSERT INTO memberships (id, user_id, tenant_id, role, active) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        params = (
            str(membership.id),
            str(membership.user_id),
            str(membership.tenant_id),
            membership.role,
            int(membership.active),
        )

        if connection is not None:
            connection.execute(query, params)
            return

        with self._database.connect() as conn:
            conn.execute(query, params)

    def find_by_id(
        self,
        membership_id: UUID,
        connection: sqlite3.Connection | None = None,
    ) -> Membership | None:
        query = (
            "SELECT id, user_id, tenant_id, role, active "
            "FROM memberships WHERE id = ?"
        )
        params = (str(membership_id),)

        if connection is not None:
            row = connection.execute(query, params).fetchone()
        else:
            with self._database.connect() as conn:
                row = conn.execute(query, params).fetchone()

        if row is None:
            return None

        return self._to_entity(row)

    def find_by_user(
        self,
        user_id: UUID,
        connection: sqlite3.Connection | None = None,
    ) -> list[Membership]:
        query = (
            "SELECT id, user_id, tenant_id, role, active "
            "FROM memberships WHERE user_id = ?"
        )
        params = (str(user_id),)

        if connection is not None:
            rows = connection.execute(query, params).fetchall()
        else:
            with self._database.connect() as conn:
                rows = conn.execute(query, params).fetchall()

        return [self._to_entity(row) for row in rows]

    def find_by_user_and_tenant(
        self,
        user_id: UUID,
        tenant_id: UUID,
        connection: sqlite3.Connection | None = None,
    ) -> Membership | None:
        query = (
            "SELECT id, user_id, tenant_id, role, active "
            "FROM memberships "
            "WHERE user_id = ? AND tenant_id = ?"
        )
        params = (str(user_id), str(tenant_id))

        if connection is not None:
            row = connection.execute(query, params).fetchone()
        else:
            with self._database.connect() as conn:
                row = conn.execute(query, params).fetchone()

        if row is None:
            return None

        return self._to_entity(row)

    @staticmethod
    def _to_entity(row) -> Membership:
        return Membership(
            UUID(row["id"]),
            UUID(row["user_id"]),
            UUID(row["tenant_id"]),
            row["role"],
            bool(row["active"]),
        )
