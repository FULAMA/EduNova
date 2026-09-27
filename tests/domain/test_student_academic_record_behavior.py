from uuid import uuid4

from src.academic.domain.entities.student_academic_record import StudentAcademicRecord
from src.academic.domain.value_objects.subject_result import SubjectResult


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


def test_add_subject_result_updates_subject_results():
    record = create_record()

    subject_result = SubjectResult(
        subject_id=uuid4(),
        average=16,
        coefficient=3,
    )

    updated_record = record.with_subject_result(subject_result)

    assert len(updated_record.subject_results) == 1
    assert updated_record.subject_results[0] == subject_result


def test_add_subject_result_calculates_general_average():
    record = create_record()

    first_subject = SubjectResult(
        subject_id=uuid4(),
        average=16,
        coefficient=3,
    )

    second_subject = SubjectResult(
        subject_id=uuid4(),
        average=10,
        coefficient=1,
    )

    updated_record = (
        record
        .with_subject_result(first_subject)
        .with_subject_result(second_subject)
    )

    assert updated_record.general_average == 14.5


def test_add_subject_result_counts_failed_subjects():
    record = create_record()

    failed_subject = SubjectResult(
        subject_id=uuid4(),
        average=8,
        coefficient=2,
    )

    passed_subject = SubjectResult(
        subject_id=uuid4(),
        average=14,
        coefficient=2,
    )

    updated_record = (
        record
        .with_subject_result(failed_subject)
        .with_subject_result(passed_subject)
    )

    assert updated_record.failed_subjects == 1


def test_add_subject_result_does_not_mutate_original_record():
    record = create_record()

    subject_result = SubjectResult(
        subject_id=uuid4(),
        average=16,
        coefficient=3,
    )

    updated_record = record.with_subject_result(subject_result)

    assert record.subject_results == ()
    assert record.general_average == 0
    assert record.failed_subjects == 0

    assert updated_record is not record
