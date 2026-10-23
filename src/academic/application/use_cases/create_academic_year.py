from datetime import date
from uuid import UUID, uuid4

from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.domain.entities.academic_year import AcademicYear


class CreateAcademicYear:
    def __init__(self, repository: AcademicYearRepository):
        self._repository = repository

    def execute(self, tenant_id: UUID, label: str, start_date: date, end_date: date) -> AcademicYear:
        year = AcademicYear(uuid4(), tenant_id, label.strip(), start_date, end_date)
        self._repository.save(year)
        return year
