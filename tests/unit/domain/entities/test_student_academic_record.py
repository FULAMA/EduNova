import pytest
from uuid import uuid4

from src.academic.domain.value_objects.subject_result import SubjectResult
from src.academic.domain.entities.student_academic_record import (
    AcademicRecordStatus,
    StudentAcademicRecord,
)


def test_student_academic_record_can_be_created():

    record = StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(),
        general_average=14.5,
        failed_subjects=1,
        credits_obtained=54,
        total_credits=60,
    )

    assert record.general_average == 14.5
    assert record.failed_subjects == 1
    assert record.credits_obtained == 54


def test_average_cannot_be_negative():

    with pytest.raises(ValueError):
        StudentAcademicRecord(
            tenant_id=uuid4(),
            student_id=uuid4(),
            academic_period_id=uuid4(),
            subject_results=(),
            general_average=-1,
            failed_subjects=0,
            credits_obtained=60,
            total_credits=60,
        )


def test_average_cannot_exceed_20():

    with pytest.raises(ValueError):
        StudentAcademicRecord(
            tenant_id=uuid4(),
            student_id=uuid4(),
            academic_period_id=uuid4(),
            subject_results=(),
            general_average=21,
            failed_subjects=0,
            credits_obtained=60,
            total_credits=60,
        )


def test_obtained_credits_cannot_exceed_total_credits():

    with pytest.raises(ValueError):
        StudentAcademicRecord(
            tenant_id=uuid4(),
            student_id=uuid4(),
            academic_period_id=uuid4(),
            subject_results=(),
            general_average=14,
            failed_subjects=0,
            credits_obtained=61,
            total_credits=60,
        )


def test_cannot_add_duplicate_subject_result():
    subject_id = uuid4()

    first_result = SubjectResult(
        subject_id=subject_id,
        average=14,
        coefficient=2,
    )

    second_result = SubjectResult(
        subject_id=subject_id,
        average=16,
        coefficient=2,
    )

    record = StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(first_result,),
        general_average=14,
        failed_subjects=0,
        credits_obtained=60,
        total_credits=60,
    )

    with pytest.raises(ValueError):
        record.with_subject_result(second_result)

def test_validated_academic_record_cannot_be_modified():
    record = StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(),
        general_average=14,
        failed_subjects=0,
        credits_obtained=60,
        total_credits=60,
    )

    validated_record = record.validate()

    result = SubjectResult(
        subject_id=uuid4(),
        average=16,
        coefficient=2,
    )

    with pytest.raises(ValueError):
        validated_record.with_subject_result(result)
def test_new_academic_record_starts_at_version_one():
    record = StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(),
        general_average=14,
        failed_subjects=0,
        credits_obtained=60,
        total_credits=60,
    )

    assert record.version == 1

def test_draft_modification_preserves_current_version():
    record = StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(),
        general_average=14,
        failed_subjects=0,
        credits_obtained=60,
        total_credits=60,
        version=3,
    )

    result = SubjectResult(
        subject_id=uuid4(),
        average=16,
        coefficient=2,
    )

    modified_record = record.with_subject_result(result)

    assert modified_record.version == 3

def test_correction_creates_new_version_without_modifying_previous_record():
    record = StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(),
        general_average=14,
        failed_subjects=0,
        credits_obtained=60,
        total_credits=60,
        status=AcademicRecordStatus.VALIDATED,
        version=1,
    )

    corrected_record = record.create_new_version(
        general_average=15,
        failed_subjects=0,
        credits_obtained=60,
    )

    assert record.version == 1
    assert record.general_average == 14

    assert corrected_record.version == 2
    assert corrected_record.general_average == 15
    assert corrected_record.tenant_id == record.tenant_id
    assert corrected_record.student_id == record.student_id
    assert corrected_record.academic_period_id == record.academic_period_id
    assert corrected_record.subject_results == record.subject_results

def test_cannot_create_new_version_from_draft():
    record = StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(),
        general_average=14,
        failed_subjects=0,
        credits_obtained=60,
        total_credits=60,
        version=1,
    )

    with pytest.raises(ValueError):
        record.create_new_version(
            general_average=15,
            failed_subjects=0,
            credits_obtained=60,
        )

