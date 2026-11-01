from uuid import UUID, uuid4

from src.academic.application.interfaces.academic_calendar_repository import (
    AcademicCalendarRepository,
)
from src.academic.domain.entities.academic_calendar import AcademicCalendar


class CreateAcademicCalendar:
    def __init__(self, calendars: AcademicCalendarRepository):
        self._calendars = calendars

    def execute(
        self, tenant_id: UUID, name: str, description: str | None = None
    ) -> AcademicCalendar:
        calendar = AcademicCalendar(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            description=description.strip() if description else None,
        )
        self._calendars.save(calendar)
        return calendar
