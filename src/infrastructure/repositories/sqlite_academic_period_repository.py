from datetime import date
from uuid import UUID

from src.academic.application.interfaces.academic_period_repository import (
    AcademicPeriodRepository,
)
from src.academic.domain.entities.academic_period import AcademicPeriod
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteAcademicPeriodRepository(AcademicPeriodRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def list_by_tenant(self, tenant_id: UUID) -> list[AcademicPeriod]:
        with self._database.connect() as connection:
            rows = connection.execute(
                "SELECT id, tenant_id, name, start_date, end_date, academic_year_id FROM academic_periods "
                "WHERE tenant_id = ? ORDER BY start_date DESC, name COLLATE NOCASE",
                (str(tenant_id),),
            ).fetchall()
        return [AcademicPeriod(UUID(row["id"]), UUID(row["tenant_id"]), row["name"],
                date.fromisoformat(row["start_date"]), date.fromisoformat(row["end_date"]),
                UUID(row["academic_year_id"]) if row["academic_year_id"] else None)
                for row in rows]

    def find_by_id(self, period_id: UUID, tenant_id: UUID) -> AcademicPeriod | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT id, tenant_id, name, start_date, end_date, academic_year_id FROM academic_periods "
                "WHERE id = ? AND tenant_id = ?", (str(period_id), str(tenant_id)),
            ).fetchone()
        if row is None:
            return None
        return AcademicPeriod(UUID(row["id"]), UUID(row["tenant_id"]), row["name"],
                              date.fromisoformat(row["start_date"]),
                              date.fromisoformat(row["end_date"]),
                              UUID(row["academic_year_id"]) if row["academic_year_id"] else None)

    def save(self, period: AcademicPeriod) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """INSERT INTO academic_periods
                   (id, tenant_id, name, start_date, end_date, academic_year_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (str(period.id), str(period.tenant_id), period.name,
                 period.start_date.isoformat(), period.end_date.isoformat(),
                 str(period.academic_year_id) if period.academic_year_id else None),
            )
