from datetime import date
from uuid import UUID, uuid4

from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.application.interfaces.attendance_repository import AttendanceRepository
from src.academic.application.interfaces.student_repository import StudentRepository
from src.academic.domain.entities.academic_year import AcademicYearStatus
from src.academic.domain.entities.attendance import Attendance, AttendanceStatus


class RecordAttendance:
    def __init__(self, attendance_repository: AttendanceRepository,
                 student_repository: StudentRepository,
                 year_repository: AcademicYearRepository,
                 period_repository: AcademicPeriodRepository):
        self._attendance = attendance_repository
        self._students = student_repository
        self._years = year_repository
        self._periods = period_repository

    def execute(self, tenant_id: UUID, student_id: UUID, academic_class_id: UUID,
                academic_year_id: UUID, academic_period_id: UUID,
                attendance_date: date, status: AttendanceStatus,
                justified: bool, actor_id: UUID) -> Attendance:
        if self._students.get_by_id_and_tenant(student_id, tenant_id) is None:
            raise ValueError("Élève introuvable dans cet établissement.")
        year = self._years.find_by_id(academic_year_id, tenant_id)
        if year is None:
            raise ValueError("Année scolaire introuvable dans cet établissement.")
        period = self._periods.find_by_id(academic_period_id, tenant_id)
        if period is None:
            raise ValueError("Période introuvable dans cet établissement.")
        if not year.start_date <= attendance_date <= year.end_date:
            raise ValueError("La date doit appartenir à l'année scolaire sélectionnée.")
        if not period.contains(attendance_date):
            raise ValueError("La date doit appartenir à la période sélectionnée.")
        if period.academic_year_id != academic_year_id:
            raise ValueError("La période ne correspond pas à l'année scolaire sélectionnée.")
        if year.status is AcademicYearStatus.DRAFT:
            raise ValueError("Les présences ne peuvent être saisies dans une année brouillon.")
        if not self._attendance.has_active_assignment(
            tenant_id, student_id, academic_class_id, academic_year_id
        ):
            raise ValueError("L'élève ne possède pas d'affectation active dans cette classe et cette année.")
        entry = Attendance(
            id=uuid4(), tenant_id=tenant_id, student_id=student_id,
            academic_class_id=academic_class_id, academic_year_id=academic_year_id,
            academic_period_id=academic_period_id, attendance_date=attendance_date,
            status=status, justified=justified, recorded_by=actor_id,
        )
        return self._attendance.record(entry)
