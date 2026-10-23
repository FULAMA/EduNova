from uuid import UUID, uuid4

import pytest

from src.academic.application.use_cases.prepare_deliberation import PrepareDeliberation
from src.academic.domain.entities.student_academic_record import (
    AcademicRecordStatus,
    StudentAcademicRecord,
)
from src.academic.domain.value_objects.subject_result import SubjectResult


TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


class FakeRecordRepository:
    def __init__(self, record):
        self.record = record

    def find_by_student_and_period(self, student_id, academic_period_id, tenant_id):
        if tenant_id != TENANT_ID:
            return None
        return self.record


def make_record(status=AcademicRecordStatus.VALIDATED, credits_obtained=0):
    return StudentAcademicRecord(
        tenant_id=TENANT_ID,
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(),
        general_average=12,
        failed_subjects=0,
        credits_obtained=credits_obtained,
        total_credits=30,
        status=status,
        version=3,
    )


def test_prepare_deliberation_uses_validated_record_and_captures_version():
    record = make_record()
    result = PrepareDeliberation(FakeRecordRepository(record)).execute(
        TENANT_ID, record.student_id, record.academic_period_id
    )

    assert result.decision.value == "ADMITTED"
    assert result.record_version == 3
    assert result.tenant_id == TENANT_ID


def test_prepare_deliberation_rejects_draft_record():
    record = make_record(AcademicRecordStatus.DRAFT)

    with pytest.raises(ValueError, match="valide"):
        PrepareDeliberation(FakeRecordRepository(record)).execute(
            TENANT_ID, record.student_id, record.academic_period_id
        )


def test_prepare_deliberation_recomputes_aggregates_from_subject_results():
    record = StudentAcademicRecord(
        tenant_id=TENANT_ID,
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(
            SubjectResult(uuid4(), 14.0, 1.0),
            SubjectResult(uuid4(), 8.0, 1.0),
        ),
        general_average=20.0,
        failed_subjects=99,
        credits_obtained=0.0,
        total_credits=30.0,
        status=AcademicRecordStatus.VALIDATED,
        version=3,
    )

    result = PrepareDeliberation(FakeRecordRepository(record)).execute(
        TENANT_ID, record.student_id, record.academic_period_id
    )

    assert result.average == 11.0
    assert result.failed_subjects == 0


def test_prepare_deliberation_does_not_use_credits_for_the_decision():
    record_without_credits = make_record(credits_obtained=0)
    record_with_credits = make_record(credits_obtained=30)

    without_credits = PrepareDeliberation(
        FakeRecordRepository(record_without_credits)
    ).execute(
        TENANT_ID,
        record_without_credits.student_id,
        record_without_credits.academic_period_id,
    )
    with_credits = PrepareDeliberation(
        FakeRecordRepository(record_with_credits)
    ).execute(
        TENANT_ID,
        record_with_credits.student_id,
        record_with_credits.academic_period_id,
    )

    assert without_credits.decision == with_credits.decision
