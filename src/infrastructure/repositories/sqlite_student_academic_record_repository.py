from sqlite3 import Connection
from uuid import UUID

from src.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.domain.entities.student_academic_record import StudentAcademicRecord
from src.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteStudentAcademicRecordRepository(
    StudentAcademicRecordRepository
):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, record: StudentAcademicRecord) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO student_academic_records (
                    student_id,
                    academic_period_id,
                    tenant_id,
                    general_average,
                    failed_subjects,
                    credits_obtained,
                    total_credits
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(record.student_id),
                    str(record.academic_period_id),
                    str(record.tenant_id),
                    record.general_average,
                    record.failed_subjects,
                    record.credits_obtained,
                    record.total_credits,
                ),
            )

            connection.execute(
                """
                DELETE FROM subject_results
                WHERE student_id = ?
                  AND academic_period_id = ?
                  AND tenant_id = ?
                """,
                (
                    str(record.student_id),
                    str(record.academic_period_id),
                    str(record.tenant_id),
                ),
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
        )




