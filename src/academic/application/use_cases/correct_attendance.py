from uuid import UUID

from src.academic.application.interfaces.attendance_repository import AttendanceRepository
from src.academic.domain.entities.attendance import Attendance, AttendanceStatus


class CorrectAttendance:
    def __init__(self, repository: AttendanceRepository):
        self._repository = repository

    def execute(
        self,
        tenant_id: UUID,
        attendance_id: UUID,
        status: AttendanceStatus,
        justified: bool,
        expected_version: int,
        changed_by: UUID,
    ) -> Attendance:
        current = self._repository.find_by_id(tenant_id, attendance_id)
        if current is None:
            raise ValueError("Releve de presence introuvable dans cet etablissement.")
        corrected = current.corrected(status, justified)
        return self._repository.correct(corrected, expected_version, changed_by)
