from datetime import date
from uuid import uuid4

import pytest

from src.domain.entities.attendance import (
    Attendance,
    AttendanceStatus,
)
from src.domain.services.attendance_analyzer import (
    AttendanceAnalyzer,
)


def create_attendance(
    status: AttendanceStatus,
    justified: bool = False,
) -> Attendance:

    return Attendance(
        id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        attendance_date=date.today(),
        status=status,
        justified=justified,
    )


def test_count_total_sessions():

    attendances = [
        create_attendance(AttendanceStatus.PRESENT),
        create_attendance(AttendanceStatus.ABSENT),
        create_attendance(AttendanceStatus.LATE),
    ]

    analyzer = AttendanceAnalyzer()

    assert analyzer.total_sessions(attendances) == 3


def test_count_absences():

    attendances = [
        create_attendance(AttendanceStatus.PRESENT),
        create_attendance(AttendanceStatus.ABSENT),
        create_attendance(AttendanceStatus.ABSENT),
        create_attendance(AttendanceStatus.LATE),
    ]

    analyzer = AttendanceAnalyzer()

    assert analyzer.count_absences(attendances) == 2


def test_count_justified_absences():

    attendances = [
        create_attendance(
            AttendanceStatus.ABSENT,
            justified=True,
        ),
        create_attendance(
            AttendanceStatus.ABSENT,
            justified=False,
        ),
    ]

    analyzer = AttendanceAnalyzer()

    assert analyzer.count_justified_absences(attendances) == 1


def test_count_unjustified_absences():

    attendances = [
        create_attendance(
            AttendanceStatus.ABSENT,
            justified=True,
        ),
        create_attendance(
            AttendanceStatus.ABSENT,
            justified=False,
        ),
        create_attendance(
            AttendanceStatus.ABSENT,
            justified=False,
        ),
    ]

    analyzer = AttendanceAnalyzer()

    assert analyzer.count_unjustified_absences(attendances) == 2


def test_count_lates():

    attendances = [
        create_attendance(AttendanceStatus.LATE),
        create_attendance(AttendanceStatus.LATE),
        create_attendance(AttendanceStatus.PRESENT),
    ]

    analyzer = AttendanceAnalyzer()

    assert analyzer.count_lates(attendances) == 2


def test_calculate_attendance_rate():

    attendances = [
        create_attendance(AttendanceStatus.PRESENT),
        create_attendance(AttendanceStatus.PRESENT),
        create_attendance(AttendanceStatus.PRESENT),
        create_attendance(AttendanceStatus.ABSENT),
    ]

    analyzer = AttendanceAnalyzer()

    assert analyzer.attendance_rate(attendances) == 75


def test_cannot_calculate_attendance_rate_without_attendances():

    analyzer = AttendanceAnalyzer()

    with pytest.raises(ValueError):
        analyzer.attendance_rate([])