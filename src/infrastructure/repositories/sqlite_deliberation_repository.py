from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.academic.application.interfaces.deliberation_repository import DeliberationRepository
from src.academic.application.exceptions import DeliberationConcurrencyError
from src.academic.domain.entities.deliberation import Deliberation, DeliberationDecision
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteDeliberationRepository(DeliberationRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, deliberation: Deliberation) -> Deliberation:
        now = deliberation.created_at or datetime.now().astimezone()
        saved = Deliberation(
            student_id=deliberation.student_id, average=deliberation.average,
            failed_subjects=deliberation.failed_subjects, decision=deliberation.decision,
            tenant_id=deliberation.tenant_id, academic_period_id=deliberation.academic_period_id,
            record_version=deliberation.record_version, id=deliberation.id or uuid4(),
            status=deliberation.status, version=deliberation.version,
            created_by=deliberation.created_by, created_at=now,
            validated_by=deliberation.validated_by, validated_at=deliberation.validated_at,
        )
        with self._database.connect() as connection:
            connection.execute("""INSERT INTO academic_deliberations
                (id, tenant_id, student_id, academic_period_id, record_version, average,
                 failed_subjects, decision, status, version, created_by, created_at,
                 validated_by, validated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                    str(saved.id), str(saved.tenant_id), str(saved.student_id),
                    str(saved.academic_period_id), saved.record_version, saved.average,
                    saved.failed_subjects, saved.decision.value, saved.status, saved.version,
                    str(saved.created_by), now.isoformat(),
                    str(saved.validated_by) if saved.validated_by else None,
                    saved.validated_at.isoformat() if saved.validated_at else None,
                ))
        return saved

    def find_by_id(self, deliberation_id, tenant_id):
        with self._database.connect() as connection:
            row = connection.execute("SELECT * FROM academic_deliberations WHERE id = ? AND tenant_id = ?", (str(deliberation_id), str(tenant_id))).fetchone()
        if row is None:
            return None
        return self._from_row(row)

    @staticmethod
    def _from_row(row):
        return Deliberation(
            student_id=UUID(row["student_id"]), average=row["average"],
            failed_subjects=row["failed_subjects"],
            decision=DeliberationDecision(row["decision"]),
            tenant_id=UUID(row["tenant_id"]),
            academic_period_id=UUID(row["academic_period_id"]),
            record_version=row["record_version"], id=UUID(row["id"]),
            status=row["status"], version=row["version"],
            created_by=UUID(row["created_by"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            validated_by=UUID(row["validated_by"]) if row["validated_by"] else None,
            validated_at=datetime.fromisoformat(row["validated_at"]) if row["validated_at"] else None,
        )

    def validate(self, deliberation_id, tenant_id, expected_version, actor_id):
        validated_at = datetime.now(timezone.utc)
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            updated = connection.execute(
                """
                UPDATE academic_deliberations
                SET status = 'VALIDATED', version = version + 1,
                    validated_by = ?, validated_at = ?
                WHERE id = ? AND tenant_id = ?
                  AND status = 'PREPARED' AND version = ?
                """,
                (
                    str(actor_id), validated_at.isoformat(),
                    str(deliberation_id), str(tenant_id), expected_version,
                ),
            )
            if updated.rowcount != 1:
                raise DeliberationConcurrencyError(
                    "La délibération a déjà été validée ou modifiée."
                )
            row = connection.execute(
                "SELECT * FROM academic_deliberations WHERE id = ? AND tenant_id = ?",
                (str(deliberation_id), str(tenant_id)),
            ).fetchone()
        return self._from_row(row)
