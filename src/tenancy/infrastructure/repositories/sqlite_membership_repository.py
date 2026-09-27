from uuid import UUID

from src.tenancy.application.interfaces.membership_repository import MembershipRepository
from src.tenancy.domain.entities.membership import Membership
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteMembershipRepository(MembershipRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, membership: Membership) -> None:
        with self._database.connect() as connection:
            connection.execute(
                "INSERT INTO memberships (id, user_id, tenant_id, role, active) VALUES (?, ?, ?, ?, ?)",
                (
                    str(membership.id),
                    str(membership.user_id),
                    str(membership.tenant_id),
                    membership.role,
                    int(membership.active),
                ),
            )

    def find_by_id(self, membership_id: UUID) -> Membership | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT id, user_id, tenant_id, role, active "
                "FROM memberships WHERE id = ?",
                (str(membership_id),),
            ).fetchone()

        if row is None:
            return None

        return self._to_entity(row)

    def find_by_user(self, user_id: UUID) -> list[Membership]:
        with self._database.connect() as connection:
            rows = connection.execute(
                "SELECT id, user_id, tenant_id, role, active "
                "FROM memberships WHERE user_id = ?",
                (str(user_id),),
            ).fetchall()

        return [self._to_entity(row) for row in rows]

    def find_by_user_and_tenant(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> Membership | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT id, user_id, tenant_id, role, active "
                "FROM memberships "
                "WHERE user_id = ? AND tenant_id = ?",
                (str(user_id), str(tenant_id)),
            ).fetchone()

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
