from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.academic_period import AcademicPeriod


class AcademicPeriodRepository(ABC):
    @abstractmethod
    def save(self, period: AcademicPeriod) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, period_id: UUID, tenant_id: UUID) -> AcademicPeriod | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_tenant(self, tenant_id: UUID) -> list[AcademicPeriod]:
        raise NotImplementedError
