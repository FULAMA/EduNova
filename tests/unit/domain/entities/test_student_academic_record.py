import pytest
from uuid import uuid4

from src.domain.entities.student_academic_record import (
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
