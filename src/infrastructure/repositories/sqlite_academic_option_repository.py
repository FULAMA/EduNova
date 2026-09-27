from uuid import UUID

from src.academic.application.interfaces.academic_option_repository import (
    AcademicOptionRepository,
)
from src.academic.domain.entities.academic_option import AcademicOption
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteAcademicOptionRepository(AcademicOptionRepository):

    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, academic_option: AcademicOption) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO academic_options (
                    id,
                    tenant_id,
                    name,
                    code,
                    active
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(academic_option.id),
                    str(academic_option.tenant_id),
                    academic_option.name,
                    academic_option.code,
                    int(academic_option.active),
                ),
            )

    def find_by_id(
        self,
        academic_option_id: UUID,
        tenant_id: UUID,
    ) -> AcademicOption | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    tenant_id,
                    name,
                    code,
                    active
                FROM academic_options
                WHERE id = ?
                  AND tenant_id = ?
                """,
                (
                    str(academic_option_id),
                    str(tenant_id),
                ),
            ).fetchone()

            if row is None:
                return None

            return AcademicOption(
                id=UUID(row["id"]),
                tenant_id=UUID(row["tenant_id"]),
                name=row["name"],
                code=row["code"],
                active=bool(row["active"]),
            )
