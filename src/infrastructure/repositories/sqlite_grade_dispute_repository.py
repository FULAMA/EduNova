from datetime import datetime
from uuid import UUID

from src.academic.application.interfaces.grade_dispute_repository import GradeDisputeRepository
from src.academic.domain.entities.grade_dispute import GradeDispute, GradeDisputeStatus
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteGradeDisputeRepository(GradeDisputeRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def student_is_active_in_tenant(self, student_id: UUID, tenant_id: UUID) -> bool:
        return self._reference_exists(
            "SELECT 1 FROM students WHERE id = ? AND tenant_id = ? AND active = 1",
            student_id,
            tenant_id,
        )

    def academic_period_exists_in_tenant(self, period_id: UUID, tenant_id: UUID) -> bool:
        return self._reference_exists(
            "SELECT 1 FROM academic_periods WHERE id = ? AND tenant_id = ?",
            period_id,
            tenant_id,
        )

    def subject_exists_in_tenant(self, subject_id: UUID, tenant_id: UUID) -> bool:
        return self._reference_exists(
            "SELECT 1 FROM subjects WHERE id = ? AND tenant_id = ?",
            subject_id,
            tenant_id,
        )

    def _reference_exists(self, query: str, reference_id: UUID, tenant_id: UUID) -> bool:
        with self._database.connect() as connection:
            return connection.execute(
                query, (str(reference_id), str(tenant_id))
            ).fetchone() is not None

    def save(self, dispute: GradeDispute) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO academic_grade_disputes (
                    id, tenant_id, student_id, academic_period_id, subject_id,
                    reason, status, submitted_by, submitted_at,
                    reviewed_by, reviewed_at, resolution_notes, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(tenant_id, id) DO UPDATE SET
                    status = excluded.status,
                    reviewed_by = excluded.reviewed_by,
                    reviewed_at = excluded.reviewed_at,
                    resolution_notes = excluded.resolution_notes,
                    resolved_at = excluded.resolved_at
                """,
                (
                    str(dispute.id),
                    str(dispute.tenant_id),
                    str(dispute.student_id),
                    str(dispute.academic_period_id),
                    str(dispute.subject_id),
                    dispute.reason,
                    dispute.status.value,
                    str(dispute.submitted_by),
                    dispute.submitted_at.isoformat(),
                    str(dispute.reviewed_by) if dispute.reviewed_by else None,
                    dispute.reviewed_at.isoformat() if dispute.reviewed_at else None,
                    dispute.resolution_notes,
                    dispute.resolved_at.isoformat() if dispute.resolved_at else None,
                ),
            )

    def find_by_id(self, dispute_id: UUID, tenant_id: UUID) -> GradeDispute | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM academic_grade_disputes
                WHERE id = ? AND tenant_id = ?
                """,
                (str(dispute_id), str(tenant_id)),
            ).fetchone()
        if row is None:
            return None
        return self._map_row(row)

    def list(
        self,
        tenant_id: UUID,
        *,
        student_id: UUID | None = None,
        academic_period_id: UUID | None = None,
        subject_id: UUID | None = None,
        status: GradeDisputeStatus | None = None,
    ) -> tuple[GradeDispute, ...]:
        filters = ["tenant_id = ?"]
        params: list[object] = [str(tenant_id)]

        if student_id is not None:
            filters.append("student_id = ?")
            params.append(str(student_id))
        if academic_period_id is not None:
            filters.append("academic_period_id = ?")
            params.append(str(academic_period_id))
        if subject_id is not None:
            filters.append("subject_id = ?")
            params.append(str(subject_id))
        if status is not None:
            filters.append("status = ?")
            params.append(status.value)

        where_clause = " AND ".join(filters)
        with self._database.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM academic_grade_disputes
                WHERE {where_clause}
                ORDER BY submitted_at DESC, id DESC
                """,
                params,
            ).fetchall()
        return tuple(self._map_row(r) for r in rows)

    @staticmethod
    def _map_row(row) -> GradeDispute:
        return GradeDispute(
            id=UUID(row["id"]),
            tenant_id=UUID(row["tenant_id"]),
            student_id=UUID(row["student_id"]),
            academic_period_id=UUID(row["academic_period_id"]),
            subject_id=UUID(row["subject_id"]),
            reason=row["reason"],
            status=GradeDisputeStatus(row["status"]),
            submitted_by=UUID(row["submitted_by"]),
            submitted_at=datetime.fromisoformat(row["submitted_at"]),
            reviewed_by=UUID(row["reviewed_by"]) if row["reviewed_by"] else None,
            reviewed_at=datetime.fromisoformat(row["reviewed_at"]) if row["reviewed_at"] else None,
            resolution_notes=row["resolution_notes"],
            resolved_at=datetime.fromisoformat(row["resolved_at"]) if row["resolved_at"] else None,
        )
