from datetime import datetime
from uuid import UUID

from src.identity.application.interfaces.student_user_link_repository import StudentUserLinkRepository
from src.identity.domain.entities.student_user_link import StudentUserLink
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteStudentUserLinkRepository(StudentUserLinkRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, link: StudentUserLink) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """INSERT INTO student_user_links
                   (tenant_id, user_id, student_id, created_by, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    str(link.tenant_id), str(link.user_id), str(link.student_id),
                    str(link.created_by), link.created_at.isoformat(),
                ),
            )

    def find_by_user(self, user_id: UUID, tenant_id: UUID) -> tuple[StudentUserLink, ...]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """SELECT tenant_id, user_id, student_id, created_by, created_at
                   FROM student_user_links
                   WHERE tenant_id = ? AND user_id = ?""",
                (str(tenant_id), str(user_id)),
            ).fetchall()
        return tuple(
            StudentUserLink(
                tenant_id=UUID(row["tenant_id"]),
                user_id=UUID(row["user_id"]),
                student_id=UUID(row["student_id"]),
                created_by=UUID(row["created_by"]),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        )

