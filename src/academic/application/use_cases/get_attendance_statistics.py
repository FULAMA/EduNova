from uuid import UUID

from src.academic.domain.services.attendance_analyzer import AttendanceAnalyzer
from src.academic.application.interfaces.attendance_repository import AttendanceRepository


class GetAttendanceStatistics:
    def __init__(self, repository: AttendanceRepository,
                 analyzer: AttendanceAnalyzer | None = None):
        self._repository = repository
        self._analyzer = analyzer or AttendanceAnalyzer()

    def execute(self, tenant_id: UUID, student_id: UUID,
                academic_period_id: UUID) -> dict[str, float | int | None]:
        entries = self._repository.list_by_student_period(
            tenant_id, student_id, academic_period_id
        )
        rate = self._analyzer.attendance_rate(entries) if entries else None
        return {
            "total_sessions": self._analyzer.total_sessions(entries),
            "absences": self._analyzer.count_absences(entries),
            "justified_absences": self._analyzer.count_justified_absences(entries),
            "unjustified_absences": self._analyzer.count_unjustified_absences(entries),
            "lates": self._analyzer.count_lates(entries),
            "attendance_rate": rate,
        }
