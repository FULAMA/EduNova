from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.academic_calendar import AcademicCalendar


class AcademicCalendarRepository(ABC):
    @abstractmethod
    def save(self, calendar: AcademicCalendar) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, calendar_id: UUID, tenant_id: UUID) -> AcademicCalendar | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_tenant(self, tenant_id: UUID) -> tuple[AcademicCalendar, ...]:
        raise NotImplementedError
