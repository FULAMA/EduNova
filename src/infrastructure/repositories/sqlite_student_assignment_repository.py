from datetime import datetime
from uuid import UUID

from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.domain.entities.student_assignment import StudentAssignment, StudentAssignmentStatus
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteStudentAssignmentRepository(StudentAssignmentRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, assignment: StudentAssignment) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO student_assignments
                    (id, tenant_id, student_id, academic_year_id,
                     academic_class_id, academic_option_id, status,
                     created_by, created_at, updated_at, closed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._values(assignment),
            )

    def find_by_id(self, assignment_id: UUID, tenant_id: UUID) -> StudentAssignment | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, tenant_id, student_id, academic_year_id,
                       academic_class_id, academic_option_id, status,
                       created_by, created_at, updated_at, closed_at
                FROM student_assignments
                WHERE id = ? AND tenant_id = ?
                """,
                (str(assignment_id), str(tenant_id)),
            ).fetchone()
        return self._to_entity(row) if row is not None else None

    def list_by_student(self, student_id: UUID, tenant_id: UUID) -> tuple[StudentAssignment, ...]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, tenant_id, student_id, academic_year_id,
                       academic_class_id, academic_option_id, status,
                       created_by, created_at, updated_at, closed_at
                FROM student_assignments
                WHERE student_id = ? AND tenant_id = ?
                ORDER BY created_at DESC, id
                """,
                (str(student_id), str(tenant_id)),
            ).fetchall()
        return tuple(self._to_entity(row) for row in rows)

    def update(self, assignment: StudentAssignment, expected_status: str) -> StudentAssignment:
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                UPDATE student_assignments
                SET status = ?, updated_at = ?, closed_at = ?
                WHERE id = ? AND tenant_id = ? AND status = ?
                """,
                (
                    assignment.status.value,
                    assignment.updated_at.isoformat(),
                    assignment.closed_at.isoformat() if assignment.closed_at else None,
                    str(assignment.id), str(assignment.tenant_id), expected_status,
                ),
            )
            if cursor.rowcount != 1:
                raise ValueError("L'affectation a deja ete modifiee ou n'existe pas.")
        return assignment

    def save_active(self, assignment: StudentAssignment) -> StudentAssignment:
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("""INSERT INTO student_assignments
                (id, tenant_id, student_id, academic_year_id, academic_class_id,
                 academic_option_id, status, created_by, created_at, updated_at, closed_at)
                VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?, ?, NULL)""", (
                    str(assignment.id), str(assignment.tenant_id), str(assignment.student_id),
                    str(assignment.academic_year_id), str(assignment.academic_class_id),
                    str(assignment.academic_option_id) if assignment.academic_option_id else None,
                    str(assignment.created_by), assignment.created_at.isoformat(), assignment.updated_at.isoformat(),
                ))
        return assignment

    @staticmethod
    def _values(assignment: StudentAssignment) -> tuple[str | None, ...]:
        return (
            str(assignment.id), str(assignment.tenant_id), str(assignment.student_id),
            str(assignment.academic_year_id), str(assignment.academic_class_id),
            str(assignment.academic_option_id) if assignment.academic_option_id else None,
            assignment.status.value, str(assignment.created_by),
            assignment.created_at.isoformat(), assignment.updated_at.isoformat(),
            assignment.closed_at.isoformat() if assignment.closed_at else None,
        )

    @staticmethod
    def _to_entity(row) -> StudentAssignment:
        return StudentAssignment(
            id=UUID(row["id"]), tenant_id=UUID(row["tenant_id"]),
            student_id=UUID(row["student_id"]), academic_year_id=UUID(row["academic_year_id"]),
            academic_class_id=UUID(row["academic_class_id"]),
            academic_option_id=UUID(row["academic_option_id"]) if row["academic_option_id"] else None,
            status=StudentAssignmentStatus(row["status"]),
            created_by=UUID(row["created_by"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            closed_at=datetime.fromisoformat(row["closed_at"]) if row["closed_at"] else None,
        )
