from datetime import datetime
from uuid import UUID

from src.identity.application.interfaces.parent_student_link_repository import (
    ParentStudentLinkRepository,
)
from src.identity.domain.entities.parent_student_link import (
    ParentStudentLink,
    RelationshipType,
)
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteParentStudentLinkRepository(ParentStudentLinkRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, link: ParentStudentLink) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO parent_student_links (
                    tenant_id, parent_user_id, student_id, relationship_type, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (tenant_id, parent_user_id, student_id) DO UPDATE SET
                    relationship_type = excluded.relationship_type,
                    created_by = excluded.created_by,
                    created_at = excluded.created_at
                """,
                (
                    str(link.tenant_id),
                    str(link.parent_user_id),
                    str(link.student_id),
                    link.relationship_type.value,
                    str(link.created_by),
                    link.created_at.isoformat(),
                ),
            )

    def list_by_parent(self, tenant_id: UUID, parent_user_id: UUID) -> tuple[ParentStudentLink, ...]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT tenant_id, parent_user_id, student_id, relationship_type, created_by, created_at
                FROM parent_student_links
                WHERE tenant_id = ? AND parent_user_id = ?
                ORDER BY created_at
                """,
                (str(tenant_id), str(parent_user_id)),
            ).fetchall()
        return tuple(self._map_row(r) for r in rows)

    def list_by_student(self, tenant_id: UUID, student_id: UUID) -> tuple[ParentStudentLink, ...]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT tenant_id, parent_user_id, student_id, relationship_type, created_by, created_at
                FROM parent_student_links
                WHERE tenant_id = ? AND student_id = ?
                ORDER BY created_at
                """,
                (str(tenant_id), str(student_id)),
            ).fetchall()
        return tuple(self._map_row(r) for r in rows)

    def is_parent_of(self, tenant_id: UUID, parent_user_id: UUID, student_id: UUID) -> bool:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT 1 FROM parent_student_links
                WHERE tenant_id = ? AND parent_user_id = ? AND student_id = ?
                """,
                (str(tenant_id), str(parent_user_id), str(student_id)),
            ).fetchone()
        return row is not None

    @staticmethod
    def _map_row(row) -> ParentStudentLink:
        return ParentStudentLink(
            tenant_id=UUID(row["tenant_id"]),
            parent_user_id=UUID(row["parent_user_id"]),
            student_id=UUID(row["student_id"]),
            relationship_type=RelationshipType(row["relationship_type"]),
            created_by=UUID(row["created_by"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
