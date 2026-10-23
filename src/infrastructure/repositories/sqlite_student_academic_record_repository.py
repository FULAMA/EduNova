import json
import sqlite3
from datetime import datetime, timezone
from sqlite3 import Connection
from uuid import UUID

from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.application.exceptions import AcademicRecordConcurrencyError
from src.academic.application.exceptions import AcademicRecordHistoryReadError
from src.academic.domain.entities.student_academic_record import (
    AcademicRecordStatus,
    StudentAcademicRecord,
)
from src.academic.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteStudentAcademicRecordRepository(
    StudentAcademicRecordRepository
):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(
        self,
        record: StudentAcademicRecord,
        *,
        expected_version: int | None = None,
        operation: str = "SAVE",
        actor_id: UUID | None = None,
        reason: str | None = None,
    ) -> None:
        with self._database.connect() as connection:
            key = (
                str(record.student_id),
                str(record.academic_period_id),
                str(record.tenant_id),
            )
            if expected_version is None:
                try:
                    connection.execute(
                        """
                        INSERT INTO student_academic_records (
                            student_id, academic_period_id, tenant_id,
                            general_average, failed_subjects, credits_obtained,
                            total_credits, version, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            *key,
                            record.general_average,
                            record.failed_subjects,
                            record.credits_obtained,
                            record.total_credits,
                            record.version,
                            record.status.value,
                        ),
                    )
                except sqlite3.IntegrityError as exc:
                    if "student_academic_records" in str(exc) and (
                        "UNIQUE constraint failed" in str(exc)
                        or "PRIMARY KEY" in str(exc)
                    ):
                        raise ValueError("Academic record already exists") from exc
                    raise
            else:
                updated = connection.execute(
                    """
                    UPDATE student_academic_records
                    SET general_average = ?, failed_subjects = ?,
                        credits_obtained = ?, total_credits = ?,
                        version = ?, status = ?
                    WHERE student_id = ? AND academic_period_id = ?
                      AND tenant_id = ? AND version = ?
                    """,
                    (
                        record.general_average,
                        record.failed_subjects,
                        record.credits_obtained,
                        record.total_credits,
                        record.version,
                        record.status.value,
                        *key,
                        expected_version,
                    ),
                )
                if updated.rowcount != 1:
                    raise AcademicRecordConcurrencyError(
                        "Le dossier académique a été modifié. Rechargez-le avant de réessayer."
                    )

            connection.execute(
                """
                DELETE FROM subject_results
                WHERE student_id = ?
                  AND academic_period_id = ?
                  AND tenant_id = ?
                """,
                key,
            )

            connection.executemany(
                """
                INSERT INTO subject_results (
                    student_id,
                    academic_period_id,
                    tenant_id,
                    subject_id,
                    average,
                    coefficient,
                    position
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        str(record.student_id),
                        str(record.academic_period_id),
                        str(record.tenant_id),
                        str(result.subject_id),
                        result.average,
                        result.coefficient,
                        position,
                    )
                    for position, result in enumerate(
                        record.subject_results
                    )
                ],
            )

            self._append_history(connection, record, operation, actor_id, reason)

    @staticmethod
    def _append_history(
        connection: Connection,
        record: StudentAcademicRecord,
        operation: str,
        actor_id: UUID | None,
        reason: str | None,
    ) -> None:
        snapshot = {
            "general_average": record.general_average,
            "failed_subjects": record.failed_subjects,
            "credits_obtained": record.credits_obtained,
            "total_credits": record.total_credits,
            "subject_results": [
                {
                    "subject_id": str(result.subject_id),
                    "average": result.average,
                    "coefficient": result.coefficient,
                }
                for result in record.subject_results
            ],
        }
        if actor_id is not None:
            snapshot["actor_id"] = str(actor_id)
        if reason is not None:
            snapshot["reason"] = reason
        try:
            connection.execute(
                """
                INSERT INTO student_academic_record_history (
                    tenant_id, student_id, academic_period_id, version,
                    status, operation, snapshot_json, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(record.tenant_id),
                    str(record.student_id),
                    str(record.academic_period_id),
                    record.version,
                    record.status.value,
                    operation,
                    json.dumps(snapshot, sort_keys=True),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        except sqlite3.OperationalError as exc:
            if "no such table" in str(exc).lower() and operation != "CORRECTED":
                return
            raise

    def list_history(self, student_id, academic_period_id, tenant_id):
        try:
            with self._database.connect() as connection:
                rows = connection.execute(
                    """
                    SELECT version, status, operation, snapshot_json, recorded_at
                    FROM student_academic_record_history
                    WHERE tenant_id = ? AND student_id = ? AND academic_period_id = ?
                    ORDER BY id
                    """,
                    (str(tenant_id), str(student_id), str(academic_period_id)),
                ).fetchall()
        except sqlite3.DatabaseError as exc:
            raise AcademicRecordHistoryReadError(
                "L'historique academique est indisponible."
            ) from exc

        entries = []
        for row in rows:
            try:
                snapshot = json.loads(row["snapshot_json"])
            except (TypeError, json.JSONDecodeError) as exc:
                raise AcademicRecordHistoryReadError(
                    "L'historique academique est indisponible."
                ) from exc
            if not isinstance(snapshot, dict):
                raise AcademicRecordHistoryReadError(
                    "L'historique academique est indisponible."
                )
            entries.append({
                "version": row["version"],
                "status": row["status"],
                "operation": row["operation"],
                "recorded_at": row["recorded_at"],
                "actor_id": snapshot.get("actor_id"),
                "reason": snapshot.get("reason"),
                "snapshot": snapshot,
            })
        return tuple(entries)

    def list_period_ids_by_student(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> tuple[UUID, ...]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT academic_period_id
                FROM student_academic_records
                WHERE student_id = ? AND tenant_id = ?
                ORDER BY academic_period_id
                """,
                (str(student_id), str(tenant_id)),
            ).fetchall()

        return tuple(UUID(row["academic_period_id"]) for row in rows)

    def find_by_student(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> StudentAcademicRecord | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM student_academic_records
                WHERE student_id = ?
                  AND tenant_id = ?
                ORDER BY academic_period_id
                LIMIT 1
                """,
                (
                    str(student_id),
                    str(tenant_id),
                ),
            ).fetchone()

            if row is None:
                return None

            return self._to_domain(connection, row)

    def find_by_student_and_period(
        self,
        student_id: UUID,
        academic_period_id: UUID,
        tenant_id: UUID,
    ) -> StudentAcademicRecord | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM student_academic_records
                WHERE student_id = ?
                  AND academic_period_id = ?
                  AND tenant_id = ?
                """,
                (
                    str(student_id),
                    str(academic_period_id),
                    str(tenant_id),
                ),
            ).fetchone()

            if row is None:
                return None

            return self._to_domain(connection, row)

    def _to_domain(
        self,
        connection: Connection,
        row,
    ) -> StudentAcademicRecord:

        subject_rows = connection.execute(
            """
            SELECT
                subject_id,
                average,
                coefficient
            FROM subject_results
            WHERE student_id = ?
              AND academic_period_id = ?
              AND tenant_id = ?
            ORDER BY position
            """,
            (
                row["student_id"],
                row["academic_period_id"],
                row["tenant_id"],
            ),
        ).fetchall()

        subject_results = tuple(
            SubjectResult(
                subject_id=UUID(subject_row["subject_id"]),
                average=subject_row["average"],
                coefficient=subject_row["coefficient"],
            )
            for subject_row in subject_rows
        )

        return StudentAcademicRecord(
            tenant_id=UUID(row["tenant_id"]),
            student_id=UUID(row["student_id"]),
            academic_period_id=UUID(row["academic_period_id"]),
            subject_results=subject_results,
            general_average=row["general_average"],
            failed_subjects=row["failed_subjects"],
            credits_obtained=row["credits_obtained"],
            total_credits=row["total_credits"],
            status=AcademicRecordStatus(row["status"]),
            version=row["version"],
        )
