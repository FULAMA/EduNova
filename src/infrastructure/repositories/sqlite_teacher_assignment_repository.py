from datetime import datetime
from uuid import UUID

from src.academic.application.interfaces.teacher_assignment_repository import (
    TeacherAssignmentRepository,
)
from src.academic.domain.entities.teacher_assignment import TeacherAssignment
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteTeacherAssignmentRepository(TeacherAssignmentRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, assignment: TeacherAssignment) -> TeacherAssignment:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO teacher_assignments (
                    tenant_id, teacher_user_id, academic_class_id, subject_id,
                    academic_year_id, assigned_by, assigned_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (tenant_id, teacher_user_id, academic_class_id, subject_id, academic_year_id)
                DO UPDATE SET
                    assigned_by = excluded.assigned_by,
                    assigned_at = excluded.assigned_at
                """,
                (
                    str(assignment.tenant_id),
                    str(assignment.teacher_user_id),
                    str(assignment.academic_class_id),
                    str(assignment.subject_id),
                    str(assignment.academic_year_id),
                    str(assignment.assigned_by),
                    assignment.assigned_at.isoformat(),
                ),
            )
        return assignment

    def list_by_teacher(
        self, tenant_id: UUID, teacher_user_id: UUID, academic_year_id: UUID | None = None,
    ) -> tuple[TeacherAssignment, ...]:
        query = """
            SELECT tenant_id, teacher_user_id, academic_class_id, subject_id,
                   academic_year_id, assigned_by, assigned_at
            FROM teacher_assignments
            WHERE tenant_id = ? AND teacher_user_id = ?
        """
        params: list[str] = [str(tenant_id), str(teacher_user_id)]
        if academic_year_id is not None:
            query += " AND academic_year_id = ?"
            params.append(str(academic_year_id))
        query += " ORDER BY assigned_at DESC"

        with self._database.connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return tuple(self._map_row(r) for r in rows)

    def list_by_class(
        self, tenant_id: UUID, academic_class_id: UUID, academic_year_id: UUID | None = None,
    ) -> tuple[TeacherAssignment, ...]:
        query = """
            SELECT tenant_id, teacher_user_id, academic_class_id, subject_id,
                   academic_year_id, assigned_by, assigned_at
            FROM teacher_assignments
            WHERE tenant_id = ? AND academic_class_id = ?
        """
        params: list[str] = [str(tenant_id), str(academic_class_id)]
        if academic_year_id is not None:
            query += " AND academic_year_id = ?"
            params.append(str(academic_year_id))
        query += " ORDER BY assigned_at DESC"

        with self._database.connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return tuple(self._map_row(r) for r in rows)

    def is_teacher_assigned(
        self,
        tenant_id: UUID,
        teacher_user_id: UUID,
        academic_class_id: UUID,
        subject_id: UUID,
        academic_year_id: UUID | None = None,
    ) -> bool:
        query = """
            SELECT 1 FROM teacher_assignments
            WHERE tenant_id = ? AND teacher_user_id = ?
              AND academic_class_id = ? AND subject_id = ?
        """
        params: list[str] = [
            str(tenant_id),
            str(teacher_user_id),
            str(academic_class_id),
            str(subject_id),
        ]
        if academic_year_id is not None:
            query += " AND academic_year_id = ?"
            params.append(str(academic_year_id))

        with self._database.connect() as connection:
            row = connection.execute(query, params).fetchone()
        return row is not None

    @staticmethod
    def _map_row(row) -> TeacherAssignment:
        return TeacherAssignment(
            tenant_id=UUID(row["tenant_id"]),
            teacher_user_id=UUID(row["teacher_user_id"]),
            academic_class_id=UUID(row["academic_class_id"]),
            subject_id=UUID(row["subject_id"]),
            academic_year_id=UUID(row["academic_year_id"]),
            assigned_by=UUID(row["assigned_by"]),
            assigned_at=datetime.fromisoformat(row["assigned_at"]),
        )
