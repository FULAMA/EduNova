from datetime import date
from uuid import UUID

from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteAcademicYearRepository(AcademicYearRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, year: AcademicYear) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO academic_years
                    (id, tenant_id, label, start_date, end_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(year.id), str(year.tenant_id), year.label,
                    year.start_date.isoformat(), year.end_date.isoformat(),
                    year.status.value,
                ),
            )

    def find_by_id(self, year_id: UUID, tenant_id: UUID) -> AcademicYear | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, tenant_id, label, start_date, end_date, status
                FROM academic_years
                WHERE id = ? AND tenant_id = ?
                """,
                (str(year_id), str(tenant_id)),
            ).fetchone()
        return self._to_entity(row) if row is not None else None

    def list_by_tenant(self, tenant_id: UUID) -> tuple[AcademicYear, ...]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, tenant_id, label, start_date, end_date, status
                FROM academic_years
                WHERE tenant_id = ?
                ORDER BY start_date DESC, label, id
                """,
                (str(tenant_id),),
            ).fetchall()
        return tuple(self._to_entity(row) for row in rows)

    def update_status(self, year: AcademicYear) -> AcademicYear:
        with self._database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE academic_years
                SET status = ?
                WHERE id = ? AND tenant_id = ?
                """,
                (year.status.value, str(year.id), str(year.tenant_id)),
            )
            if cursor.rowcount != 1:
                raise ValueError("L'annee scolaire n'existe pas ou n'a pas pu etre mise a jour.")
        return year

    @staticmethod
    def _to_entity(row) -> AcademicYear:
        return AcademicYear(
            id=UUID(row["id"]),
            tenant_id=UUID(row["tenant_id"]),
            label=row["label"],
            start_date=date.fromisoformat(row["start_date"]),
            end_date=date.fromisoformat(row["end_date"]),
            status=AcademicYearStatus(row["status"]),
        )
