from uuid import UUID

from src.application.interfaces.academic_class_repository import (
    AcademicClassRepository,
)
from src.domain.entities.academic_class import AcademicClass
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteAcademicClassRepository(AcademicClassRepository):

    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, academic_class: AcademicClass) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO academic_classes (
                    id,
                    tenant_id,
                    name
                )
                VALUES (?, ?, ?)
                """,
                (
                    str(academic_class.id),
                    str(academic_class.tenant_id),
                    academic_class.name,
                ),
            )

    def find_by_id(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
    ) -> AcademicClass | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    tenant_id,
                    name
                FROM academic_classes
                WHERE id = ?
                AND tenant_id = ?
                """,
                (
                    str(academic_class_id),
                    str(tenant_id),
                ),
            ).fetchone()

            if row is None:
                return None

            return AcademicClass(
                id=UUID(row["id"]),
                tenant_id=UUID(row["tenant_id"]),
                name=row["name"],
            )
