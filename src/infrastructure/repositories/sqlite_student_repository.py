from uuid import UUID

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.application.interfaces.student_repository import (
    StudentRepository,
)
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteStudentRepository(StudentRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def list_by_tenant(self, tenant_id: UUID) -> tuple[StudentSummary, ...]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, first_name, last_name, email, active
                FROM students
                WHERE tenant_id = ?
                ORDER BY last_name, first_name, id
                """,
                (str(tenant_id),),
            ).fetchall()

        return tuple(
            StudentSummary(
                id=UUID(row["id"]),
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                active=bool(row["active"]),
            )
            for row in rows
        )

    def get_by_id_and_tenant(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> StudentSummary | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, first_name, last_name, email, active
                FROM students
                WHERE id = ? AND tenant_id = ?
                """,
                (str(student_id), str(tenant_id)),
            ).fetchone()

        if row is None:
            return None

        return StudentSummary(
            id=UUID(row["id"]),
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            active=bool(row["active"]),
        )
