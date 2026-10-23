from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.academic_year import AcademicYear


class AcademicYearRepository(ABC):
    @abstractmethod
    def save(self, year: AcademicYear) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, year_id: UUID, tenant_id: UUID) -> AcademicYear | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_tenant(self, tenant_id: UUID) -> tuple[AcademicYear, ...]:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, year: AcademicYear) -> AcademicYear:
        raise NotImplementedError
