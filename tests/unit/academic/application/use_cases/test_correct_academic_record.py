from uuid import uuid4

from src.academic.application.dto.correct_academic_record_request import (
    CorrectAcademicRecordRequest,
)
from src.academic.application.use_cases.correct_academic_record import (
    CorrectAcademicRecord,
)
from src.academic.domain.entities.student_academic_record import (
    AcademicRecordStatus,
    StudentAcademicRecord,
)
from src.academic.domain.value_objects.subject_result import SubjectResult


class FakeAcademicRecordRepository:
    def __init__(self, record):
        self.record = record

    def find_by_student_and_period(self, student_id, academic_period_id, tenant_id):
        if (
            self.record.student_id == student_id
            and self.record.academic_period_id == academic_period_id
            and self.record.tenant_id == tenant_id
        ):
            return self.record
        return None

    def save(
        self,
        record,
        *,
        expected_version=None,
        operation="SAVE",
        actor_id=None,
        reason=None,
    ):
        assert expected_version == self.record.version
        assert operation == "CORRECTED"
        assert actor_id is not None
        assert reason == "Correction de test"
        self.record = record


def test_correction_recomputes_aggregates_instead_of_using_client_values():
    tenant_id, student_id, period_id = uuid4(), uuid4(), uuid4()
    record = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(
            SubjectResult(uuid4(), 14.0, 1.0),
            SubjectResult(uuid4(), 8.0, 1.0),
        ),
        general_average=11.0,
        failed_subjects=0,
        credits_obtained=0.0,
        total_credits=30.0,
        status=AcademicRecordStatus.VALIDATED,
        version=2,
    )
    repository = FakeAcademicRecordRepository(record)

    corrected = CorrectAcademicRecord(repository).execute(
        CorrectAcademicRecordRequest(
            tenant_id=tenant_id,
            student_id=student_id,
            academic_period_id=period_id,
            expected_version=2,
            actor_id=uuid4(),
            reason="Correction de test",
            general_average=20.0,
            failed_subjects=99,
            credits_obtained=30.0,
        )
    )

    assert corrected.general_average == 11.0
    assert corrected.failed_subjects == 0
    assert corrected.credits_obtained == 0.0
    assert corrected.version == 3
