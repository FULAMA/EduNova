from uuid import UUID

from src.academic.application.exceptions import ActiveConflictError
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus


class ChangeAcademicYearStatus:
    def __init__(self, repository: AcademicYearRepository):
        self._repository = repository

    def activate(self, year_id: UUID, tenant_id: UUID) -> AcademicYear:
        year = self._get(year_id, tenant_id)
        existing_years = self._repository.list_by_tenant(tenant_id)
        if any(y.status is AcademicYearStatus.ACTIVE and y.id != year.id for y in existing_years):
            raise ActiveConflictError("Une autre annee scolaire est deja active dans cet etablissement.")
        active = year.activate()
        self._repository.update_status(active)
        return active

    def close(self, year_id: UUID, tenant_id: UUID) -> AcademicYear:
        year = self._get(year_id, tenant_id)
        closed = year.close()
        self._repository.update_status(closed)
        return closed

    def _get(self, year_id: UUID, tenant_id: UUID) -> AcademicYear:
        year = self._repository.find_by_id(year_id, tenant_id)
        if year is None:
            raise ValueError("Annee scolaire introuvable.")
        if year.status is AcademicYearStatus.CLOSED:
            raise ValueError("Une annee cloturee ne peut pas etre rouverte.")
        return year
