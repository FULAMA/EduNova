from datetime import date
from uuid import UUID

from src.academic.application.dto.attendance_roster_entry import AttendanceRosterEntry
from src.academic.application.interfaces.attendance_repository import AttendanceRepository
from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository


class ListClassAttendance:
    def __init__(self, repository: AttendanceRepository,
                 periods: AcademicPeriodRepository):
        self._repository = repository
        self._periods = periods

    def execute(self, tenant_id: UUID, academic_class_id: UUID,
                academic_period_id: UUID, attendance_date: date) -> tuple[AttendanceRosterEntry, ...]:
        records = self._repository.list_by_class_date(
            tenant_id, academic_class_id, academic_period_id, attendance_date
        )
        period = self._periods.find_by_id(academic_period_id, tenant_id)
        if period is None or period.academic_year_id is None:
            raise ValueError("La période n'est liée à aucune année scolaire.")
        if not period.contains(attendance_date):
            raise ValueError("La date doit appartenir à la période sélectionnée.")
        academic_year_id = period.academic_year_id
        marked = {record.student_id: record for record in records}
        return tuple(
            AttendanceRosterEntry(
                student_id, first_name, last_name,
                marked[student_id].status if student_id in marked else None,
                marked[student_id].justified if student_id in marked else False,
            )
            for student_id, first_name, last_name in self._repository.list_active_roster(
                tenant_id, academic_class_id, academic_year_id
            )
        )

