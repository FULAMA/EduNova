from uuid import UUID

from src.academic.application.interfaces.attendance_repository import AttendanceRepository
from src.academic.domain.entities.attendance import Attendance


class ListStudentAttendance:
    def __init__(self, repository: AttendanceRepository):
        self._repository = repository

    def execute(
        self, tenant_id: UUID, student_id: UUID, academic_period_id: UUID
    ) -> tuple[Attendance, ...]:
        return self._repository.list_by_student_period(
            tenant_id, student_id, academic_period_id
        )
