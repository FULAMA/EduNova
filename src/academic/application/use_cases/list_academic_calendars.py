from uuid import UUID

from src.academic.application.interfaces.academic_calendar_repository import (
    AcademicCalendarRepository,
)
from src.academic.domain.entities.academic_calendar import AcademicCalendar


class ListAcademicCalendars:
    def __init__(self, calendars: AcademicCalendarRepository):
        self._calendars = calendars

    def execute(self, tenant_id: UUID) -> tuple[AcademicCalendar, ...]:
        return self._calendars.list_by_tenant(tenant_id)
