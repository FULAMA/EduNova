from uuid import UUID

from src.academic.application.interfaces.class_subject_repository import (
    ClassSubjectRepository,
)
from src.academic.domain.entities.class_subject import ClassSubject
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteClassSubjectRepository(ClassSubjectRepository):

    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, class_subject: ClassSubject) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO class_subjects (
                    id,
                    tenant_id,
                    academic_class_id,
                    subject_id,
                    coefficient,
                    academic_option_id,
                    active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(class_subject.id),
                    str(class_subject.tenant_id),
                    str(class_subject.academic_class_id),
                    str(class_subject.subject_id),
                    class_subject.coefficient,
                    (
                        str(class_subject.academic_option_id)
                        if class_subject.academic_option_id is not None
                        else None
                    ),
                    int(class_subject.active),
                ),
            )

    def find_by_id(
        self,
        class_subject_id: UUID,
        tenant_id: UUID,
    ) -> ClassSubject | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    tenant_id,
                    academic_class_id,
                    subject_id,
                    coefficient,
                    academic_option_id,
                    active
                FROM class_subjects
                WHERE id = ?
                  AND tenant_id = ?
                """,
                (
                    str(class_subject_id),
                    str(tenant_id),
                ),
            ).fetchone()

            if row is None:
                return None

            return self._to_domain(row)

    def find_by_class(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
    ) -> list[ClassSubject]:

        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    tenant_id,
                    academic_class_id,
                    subject_id,
                    coefficient,
                    academic_option_id,
                    active
                FROM class_subjects
                WHERE academic_class_id = ?
                  AND tenant_id = ?
                ORDER BY rowid
                """,
                (
                    str(academic_class_id),
                    str(tenant_id),
                ),
            ).fetchall()

            return [
                self._to_domain(row)
                for row in rows
            ]

    def find_by_class_and_option(
        self,
        academic_class_id: UUID,
        academic_option_id: UUID | None,
        tenant_id: UUID,
    ) -> list[ClassSubject]:

        with self._database.connect() as connection:

            if academic_option_id is None:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        tenant_id,
                        academic_class_id,
                        subject_id,
                        coefficient,
                        academic_option_id,
                        active
                    FROM class_subjects
                    WHERE academic_class_id = ?
                      AND tenant_id = ?
                      AND academic_option_id IS NULL
                    ORDER BY rowid
                    """,
                    (
                        str(academic_class_id),
                        str(tenant_id),
                    ),
                ).fetchall()

            else:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        tenant_id,
                        academic_class_id,
                        subject_id,
                        coefficient,
                        academic_option_id,
                        active
                    FROM class_subjects
                    WHERE academic_class_id = ?
                      AND tenant_id = ?
                      AND academic_option_id = ?
                    ORDER BY rowid
                    """,
                    (
                        str(academic_class_id),
                        str(tenant_id),
                        str(academic_option_id),
                    ),
                ).fetchall()

            return [
                self._to_domain(row)
                for row in rows
            ]

    @staticmethod
    def _to_domain(row) -> ClassSubject:
        return ClassSubject(
            id=UUID(row["id"]),
            tenant_id=UUID(row["tenant_id"]),
            academic_class_id=UUID(row["academic_class_id"]),
            subject_id=UUID(row["subject_id"]),
            coefficient=row["coefficient"],
            academic_option_id=(
                UUID(row["academic_option_id"])
                if row["academic_option_id"] is not None
                else None
            ),
            active=bool(row["active"]),
        )