from datetime import date
from uuid import UUID, uuid4

import pytest

from src.academic.application.use_cases.analyze_student_academic_risk import AnalyzeStudentAcademicRisk
from src.academic.application.use_cases.correct_attendance import CorrectAttendance
from src.academic.domain.entities.attendance import Attendance, AttendanceStatus
from src.academic.domain.entities.student_academic_record import StudentAcademicRecord


TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


class FakeAttendanceRepository:
    def __init__(self, entries: tuple[Attendance, ...]):
        self.entries = entries
        self.saved_actor = None

    def list_by_student_period(self, tenant_id, student_id, academic_period_id):
        return self.entries if tenant_id == TENANT_ID else ()

    def find_by_id(self, tenant_id, attendance_id):
        return self.entries[0] if self.entries and self.entries[0].id == attendance_id else None

    def has_active_assignment(self, tenant_id, student_id, academic_class_id, academic_year_id):
        return tenant_id == TENANT_ID

    def correct(self, attendance, expected_version, changed_by):
        if expected_version != self.entries[0].version:
            raise ValueError("Releve deja modifie")
        self.saved_actor = changed_by
        self.entries = (attendance,)
        return attendance


class FakeRecordRepository:
    def __init__(self, record):
        self.record = record

    def find_by_student_and_period(self, student_id, academic_period_id, tenant_id):
        return self.record if tenant_id == TENANT_ID else None


def make_attendance(status: AttendanceStatus, version: int = 1) -> Attendance:
    return Attendance(
        uuid4(), TENANT_ID, uuid4(), uuid4(), uuid4(), uuid4(),
        date(2026, 10, 19), status, recorded_by=uuid4(), version=version,
    )


def test_risk_uses_persisted_attendance_and_record_average():
    student_id = uuid4()
    period_id = uuid4()
    entries = (make_attendance(AttendanceStatus.PRESENT), make_attendance(AttendanceStatus.ABSENT))
    result = AnalyzeStudentAcademicRisk(
        FakeRecordRepository(StudentAcademicRecord(
            TENANT_ID, student_id, period_id, (), 9, 1, 0, 30,
        )),
        FakeAttendanceRepository(entries),
    ).execute(TENANT_ID, student_id, period_id)

    assert result.score == 70
    assert len(result.reasons) == 3


def test_correction_preserves_recorded_by_and_passes_corrector():
    current = make_attendance(AttendanceStatus.ABSENT)
    repository = FakeAttendanceRepository((current,))
    corrector = uuid4()

    corrected = CorrectAttendance(repository).execute(
        TENANT_ID, current.id, AttendanceStatus.PRESENT, False, 1, corrector
    )

    assert corrected.recorded_by == current.recorded_by
    assert corrected.version == 2
    assert repository.saved_actor == corrector


def test_correction_rejects_stale_version():
    current = make_attendance(AttendanceStatus.ABSENT, version=2)
    repository = FakeAttendanceRepository((current,))

    with pytest.raises(ValueError, match="modifie"):
        CorrectAttendance(repository).execute(
            TENANT_ID, current.id, AttendanceStatus.PRESENT, False, 1, uuid4()
        )
