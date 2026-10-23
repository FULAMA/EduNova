from datetime import date
from uuid import UUID, uuid4

from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.domain.entities.academic_period import AcademicPeriod
from src.academic.domain.entities.academic_year import AcademicYearStatus


class CreateAcademicPeriod:
    def __init__(self, periods: AcademicPeriodRepository, years: AcademicYearRepository):
        self._periods = periods
        self._years = years

    def execute(
        self, tenant_id: UUID, academic_year_id: UUID, name: str,
        start_date: date, end_date: date,
    ) -> AcademicPeriod:
        year = self._years.find_by_id(academic_year_id, tenant_id)
        if year is None:
            raise ValueError("Annee scolaire introuvable dans cet etablissement.")
        if year.status is AcademicYearStatus.CLOSED:
            raise ValueError("Une periode ne peut pas etre ajoutee a une annee cloturee.")
        if start_date < year.start_date or end_date > year.end_date:
            raise ValueError("La periode doit etre comprise dans les dates de l'annee scolaire.")
        period = AcademicPeriod(
            id=uuid4(), tenant_id=tenant_id, name=name.strip(),
            start_date=start_date, end_date=end_date,
            academic_year_id=academic_year_id,
        )
        self._periods.save(period)
        return period
