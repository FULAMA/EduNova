from uuid import UUID

from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.domain.entities.academic_year import AcademicYear


class ListAcademicYears:
    def __init__(self, repository: AcademicYearRepository):
        self._repository = repository

    def execute(self, tenant_id: UUID) -> tuple[AcademicYear, ...]:
        return self._repository.list_by_tenant(tenant_id)
