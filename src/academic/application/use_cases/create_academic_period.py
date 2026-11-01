from datetime import date
from uuid import UUID, uuid4

from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.application.interfaces.academic_calendar_repository import AcademicCalendarRepository
from src.academic.domain.entities.academic_period import AcademicPeriod
from src.academic.domain.entities.academic_year import AcademicYearStatus


class CreateAcademicPeriod:
    def __init__(self, periods: AcademicPeriodRepository, years: AcademicYearRepository, calendars: AcademicCalendarRepository | None = None):
        self._periods = periods
        self._years = years
        self._calendars = calendars

    def execute(
        self, tenant_id: UUID, academic_year_id: UUID, name: str,
        start_date: date, end_date: date, academic_calendar_id: UUID | None = None,
    ) -> AcademicPeriod:
        year = self._years.find_by_id(academic_year_id, tenant_id)
        if year is None:
            raise ValueError("Annee scolaire introuvable dans cet etablissement.")
        if year.status is AcademicYearStatus.CLOSED:
            raise ValueError("Une periode ne peut pas etre ajoutee a une annee cloturee.")
        if start_date < year.start_date or end_date > year.end_date:
            raise ValueError("La periode doit etre comprise dans les dates de l'annee scolaire.")
        if academic_calendar_id is None or self._calendars is None:
            raise ValueError("Un calendrier academique actif est obligatoire pour creer une periode.")
        calendar = self._calendars.find_by_id(academic_calendar_id, tenant_id)
        if calendar is None or not calendar.is_active:
            raise ValueError("Calendrier academique introuvable ou inactif dans cet etablissement.")
        for existing in self._periods.list_by_tenant(tenant_id):
            if existing.academic_calendar_id == academic_calendar_id and start_date <= existing.end_date and existing.start_date <= end_date:
                raise ValueError("Les periodes d'un meme calendrier ne peuvent pas se chevaucher.")
        period = AcademicPeriod(
            id=uuid4(), tenant_id=tenant_id, name=name.strip(),
            start_date=start_date, end_date=end_date,
            academic_year_id=academic_year_id,
            academic_calendar_id=academic_calendar_id,
        )
        self._periods.save(period)
        return period
