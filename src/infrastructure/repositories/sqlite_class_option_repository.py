from uuid import UUID

from src.academic.application.interfaces.class_option_repository import (
    ClassOptionRepository,
)
from src.academic.domain.entities.class_option import ClassOption
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteClassOptionRepository(ClassOptionRepository):

    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, class_option: ClassOption) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO class_options (
                    id,
                    tenant_id,
                    academic_class_id,
                    academic_option_id,
                    active
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(class_option.id),
                    str(class_option.tenant_id),
                    str(class_option.academic_class_id),
                    str(class_option.academic_option_id),
                    int(class_option.active),
                ),
            )

    def find_by_id(
        self,
        class_option_id: UUID,
        tenant_id: UUID,
    ) -> ClassOption | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    tenant_id,
                    academic_class_id,
                    academic_option_id,
                    active
                FROM class_options
                WHERE id = ?
                  AND tenant_id = ?
                """,
                (
                    str(class_option_id),
                    str(tenant_id),
                ),
            ).fetchone()

            if row is None:
                return None

            return ClassOption(
                id=UUID(row["id"]),
                tenant_id=UUID(row["tenant_id"]),
                academic_class_id=UUID(row["academic_class_id"]),
                academic_option_id=UUID(row["academic_option_id"]),
                active=bool(row["active"]),
            )

    def find_by_class_and_option(
        self,
        academic_class_id: UUID,
        academic_option_id: UUID,
        tenant_id: UUID,
    ) -> ClassOption | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    tenant_id,
                    academic_class_id,
                    academic_option_id,
                    active
                FROM class_options
                WHERE academic_class_id = ?
                  AND academic_option_id = ?
                  AND tenant_id = ?
                """,
                (
                    str(academic_class_id),
                    str(academic_option_id),
                    str(tenant_id),
                ),
            ).fetchone()

            if row is None:
                return None

            return ClassOption(
                id=UUID(row["id"]),
                tenant_id=UUID(row["tenant_id"]),
                academic_class_id=UUID(row["academic_class_id"]),
                academic_option_id=UUID(row["academic_option_id"]),
                active=bool(row["active"]),
            )