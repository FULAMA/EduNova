from uuid import UUID

from src.academic.application.interfaces.academic_period_repository import (
    AcademicPeriodRepository,
)
from src.academic.domain.entities.academic_period import AcademicPeriod


class ListAcademicPeriods:
    def __init__(self, repository: AcademicPeriodRepository):
        self._repository = repository

    def execute(self, tenant_id: UUID) -> list[AcademicPeriod]:
        return self._repository.list_by_tenant(tenant_id)
