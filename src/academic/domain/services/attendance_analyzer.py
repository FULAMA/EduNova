from collections.abc import Iterable

from src.academic.domain.entities.attendance import (
    Attendance,
    AttendanceStatus,
)


class AttendanceAnalyzer:

    def total_sessions(
        self,
        attendances: Iterable[Attendance],
    ) -> int:
        return len(list(attendances))

    def count_absences(
        self,
        attendances: Iterable[Attendance],
    ) -> int:
        return sum(
            attendance.status == AttendanceStatus.ABSENT
            for attendance in attendances
        )

    def count_justified_absences(
        self,
        attendances: Iterable[Attendance],
    ) -> int:
        return sum(
            attendance.status == AttendanceStatus.ABSENT
            and attendance.justified
            for attendance in attendances
        )

    def count_unjustified_absences(
        self,
        attendances: Iterable[Attendance],
    ) -> int:
        return sum(
            attendance.status == AttendanceStatus.ABSENT
            and not attendance.justified
            for attendance in attendances
        )

    def count_lates(
        self,
        attendances: Iterable[Attendance],
    ) -> int:
        return sum(
            attendance.status == AttendanceStatus.LATE
            for attendance in attendances
        )

    def attendance_rate(
        self,
        attendances: Iterable[Attendance],
    ) -> float:

        attendances = list(attendances)

        if not attendances:
            raise ValueError(
                "Impossible de calculer le taux "
                "d'assiduité sans présence."
            )

        present_count = sum(
            attendance.status == AttendanceStatus.PRESENT
            for attendance in attendances
        )

        return (present_count / len(attendances)) * 100