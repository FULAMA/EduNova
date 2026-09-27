from uuid import uuid4

import pytest

from src.academic.application.dto.add_subject_result_request import (
    AddSubjectResultRequest,
)
from src.academic.application.use_cases.add_subject_result import (
    AddSubjectResult,
)
from src.academic.domain.entities.student_academic_record import StudentAcademicRecord


class FakeAcademicRecordRepository:
    def __init__(self):
        self.records = {}

    def save(self, record):
        key = (
            record.tenant_id,
            record.student_id,
            record.academic_period_id,
        )
        self.records[key] = record

    def find_by_student_and_period(
        self,
        student_id,
        academic_period_id,
        tenant_id,
    ):
        return self.records.get(
            (tenant_id, student_id, academic_period_id)
        )


def create_record():
    return StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(),
        general_average=0,
        failed_subjects=0,
        credits_obtained=0,
        total_credits=30,
    )


def test_add_subject_result_updates_record():
    repository = FakeAcademicRecordRepository()
    record = create_record()
    repository.save(record)

    use_case = AddSubjectResult(repository)

    subject_id = uuid4()

    response = use_case.execute(
        AddSubjectResultRequest(
            tenant_id=record.tenant_id,
            student_id=record.student_id,
            academic_period_id=record.academic_period_id,
            subject_id=subject_id,
            average=16,
            coefficient=3,
        )
    )

    updated_record = repository.find_by_student_and_period(
        record.student_id,
        record.academic_period_id,
        record.tenant_id,
    )

    assert response.subject_id == subject_id
    assert response.average == 16
    assert response.coefficient == 3

    assert len(updated_record.subject_results) == 1
    assert updated_record.subject_results[0].subject_id == subject_id
    assert updated_record.general_average == 16
    assert updated_record.failed_subjects == 0


def test_add_subject_result_counts_failed_subject():
    repository = FakeAcademicRecordRepository()
    record = create_record()
    repository.save(record)

    use_case = AddSubjectResult(repository)

    use_case.execute(
        AddSubjectResultRequest(
            tenant_id=record.tenant_id,
            student_id=record.student_id,
            academic_period_id=record.academic_period_id,
            subject_id=uuid4(),
            average=8,
            coefficient=2,
        )
    )

    updated_record = repository.find_by_student_and_period(
        record.student_id,
        record.academic_period_id,
        record.tenant_id,
    )

    assert updated_record.failed_subjects == 1


def test_add_subject_result_requires_existing_record():
    repository = FakeAcademicRecordRepository()
    use_case = AddSubjectResult(repository)

    with pytest.raises(ValueError, match=r"Aucun dossier acad.*mique"):
        use_case.execute(
            AddSubjectResultRequest(
                tenant_id=uuid4(),
                student_id=uuid4(),
                academic_period_id=uuid4(),
                subject_id=uuid4(),
                average=15,
                coefficient=2,
            )
        )


def test_add_subject_result_preserves_original_record():
    repository = FakeAcademicRecordRepository()
    record = create_record()
    repository.save(record)

    use_case = AddSubjectResult(repository)

    use_case.execute(
        AddSubjectResultRequest(
            tenant_id=record.tenant_id,
            student_id=record.student_id,
            academic_period_id=record.academic_period_id,
            subject_id=uuid4(),
            average=15,
            coefficient=2,
        )
    )

    assert record.subject_results == ()
    assert record.general_average == 0
    assert record.failed_subjects == 0

def test_add_subject_result_rejects_invalid_average():
    repository = FakeAcademicRecordRepository()
    record = create_record()
    repository.save(record)

    use_case = AddSubjectResult(repository)

    with pytest.raises(
        ValueError,
        match=r"La moyenne doit .tre comprise entre 0 et 20",
    ):
        use_case.execute(
            AddSubjectResultRequest(
                tenant_id=record.tenant_id,
                student_id=record.student_id,
                academic_period_id=record.academic_period_id,
                subject_id=uuid4(),
                average=25,
                coefficient=2,
            )
        )


def test_add_subject_result_rejects_invalid_coefficient():
    repository = FakeAcademicRecordRepository()
    record = create_record()
    repository.save(record)

    use_case = AddSubjectResult(repository)

    with pytest.raises(
        ValueError,
        match=r"Le coefficient doit .tre sup.rieur . z.ro",
    ):
        use_case.execute(
            AddSubjectResultRequest(
                tenant_id=record.tenant_id,
                student_id=record.student_id,
                academic_period_id=record.academic_period_id,
                subject_id=uuid4(),
                average=15,
                coefficient=0,
            )
        )
