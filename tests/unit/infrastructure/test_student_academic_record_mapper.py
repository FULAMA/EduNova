from uuid import uuid4

from src.academic.domain.entities.student_academic_record import StudentAcademicRecord
from src.academic.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.persistence.student_academic_record_mapper import (
    StudentAcademicRecordMapper,
)


def create_record():
    return StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(
            SubjectResult(
                subject_id=uuid4(),
                average=15.0,
                coefficient=2.0,
            ),
        ),
        general_average=15.0,
        failed_subjects=1,
        credits_obtained=25.0,
        total_credits=30.0,
    )


def test_mapper_converts_domain_entity_to_dict():
    record = create_record()

    data = StudentAcademicRecordMapper.to_dict(record)

    assert data["student_id"] == str(record.student_id)
    assert data["tenant_id"] == str(record.tenant_id)
    assert data["academic_period_id"] == str(record.academic_period_id)
    assert data["general_average"] == 15.0
    assert data["failed_subjects"] == 1
    assert data["credits_obtained"] == 25.0
    assert data["total_credits"] == 30.0

    assert len(data["subject_results"]) == 1
    assert data["subject_results"][0]["average"] == 15.0


def test_mapper_reconstructs_domain_entity():
    record = create_record()

    data = StudentAcademicRecordMapper.to_dict(record)

    reconstructed = StudentAcademicRecordMapper.to_domain(data)

    assert reconstructed == record


def test_mapper_preserves_subject_results():
    record = create_record()

    data = StudentAcademicRecordMapper.to_dict(record)

    reconstructed = StudentAcademicRecordMapper.to_domain(data)

    assert len(reconstructed.subject_results) == 1
    assert (
        reconstructed.subject_results[0].subject_id
        == record.subject_results[0].subject_id
    )
    assert (
        reconstructed.subject_results[0].average
        == record.subject_results[0].average
    )
    assert (
        reconstructed.subject_results[0].coefficient
        == record.subject_results[0].coefficient
    )

