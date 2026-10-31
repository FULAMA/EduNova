from uuid import UUID

from src.academic.application.interfaces.academic_calendar_repository import (
    AcademicCalendarRepository,
)
from src.academic.domain.entities.academic_calendar import AcademicCalendar
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteAcademicCalendarRepository(AcademicCalendarRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, calendar: AcademicCalendar) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO academic_calendars
                    (id, tenant_id, name, description, is_active)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(calendar.id),
                    str(calendar.tenant_id),
                    calendar.name,
                    calendar.description,
                    int(calendar.is_active),
                ),
            )

    def find_by_id(
        self, calendar_id: UUID, tenant_id: UUID
    ) -> AcademicCalendar | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, tenant_id, name, description, is_active
                FROM academic_calendars
                WHERE id = ? AND tenant_id = ?
                """,
                (str(calendar_id), str(tenant_id)),
            ).fetchone()
        return self._to_entity(row) if row is not None else None

    def list_by_tenant(self, tenant_id: UUID) -> tuple[AcademicCalendar, ...]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, tenant_id, name, description, is_active
                FROM academic_calendars
                WHERE tenant_id = ?
                ORDER BY name COLLATE NOCASE, id
                """,
                (str(tenant_id),),
            ).fetchall()
        return tuple(self._to_entity(row) for row in rows)

    @staticmethod
    def _to_entity(row) -> AcademicCalendar:
        return AcademicCalendar(
            id=UUID(row["id"]),
            tenant_id=UUID(row["tenant_id"]),
            name=row["name"],
            description=row["description"],
            is_active=bool(row["is_active"]),
        )
