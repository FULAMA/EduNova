from datetime import date
from uuid import uuid4

import pytest

from src.academic.domain.entities.attendance import (
    Attendance,
    AttendanceStatus,
)


def test_student_can_be_marked_present():

    attendance = Attendance(
        id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        attendance_date=date.today(),
        status=AttendanceStatus.PRESENT,
    )

    assert attendance.status == AttendanceStatus.PRESENT
    assert attendance.is_absent is False
    assert attendance.is_late is False


def test_student_can_be_marked_absent():

    attendance = Attendance(
        id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        attendance_date=date.today(),
        status=AttendanceStatus.ABSENT,
    )

    assert attendance.is_absent is True


def test_student_can_be_marked_late():

    attendance = Attendance(
        id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        attendance_date=date.today(),
        status=AttendanceStatus.LATE,
    )

    assert attendance.is_late is True


def test_absence_can_be_justified():

    attendance = Attendance(
        id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        attendance_date=date.today(),
        status=AttendanceStatus.ABSENT,
        justified=True,
    )

    assert attendance.is_absent is True
    assert attendance.justified is True


def test_present_student_cannot_have_justified_absence():

    with pytest.raises(ValueError):

        Attendance(
            id=uuid4(),
            student_id=uuid4(),
            academic_period_id=uuid4(),
            attendance_date=date.today(),
            status=AttendanceStatus.PRESENT,
            justified=True,
        )