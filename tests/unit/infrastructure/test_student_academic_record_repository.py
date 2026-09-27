from uuid import uuid4

from src.academic.domain.entities.student_academic_record import StudentAcademicRecord
from src.academic.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.repositories.in_memory_student_academic_record_repository import (
    InMemoryStudentAcademicRecordRepository,
)


def create_record(
    tenant_id=None,
    student_id=None,
    academic_period_id=None,
    general_average=14.0,
):
    return StudentAcademicRecord(
        tenant_id=tenant_id or uuid4(),
        student_id=student_id or uuid4(),
        academic_period_id=academic_period_id or uuid4(),
        subject_results=(
            SubjectResult(
                subject_id=uuid4(),
                average=14.0,
                coefficient=2.0,
            ),
        ),
        general_average=general_average,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )


def test_repository_can_save_record():
    repository = InMemoryStudentAcademicRecordRepository()
    record = create_record()

    repository.save(record)

    result = repository.find_by_student_and_period(
        record.student_id,
        record.academic_period_id,
        record.tenant_id,
    )

    assert result == record


def test_repository_returns_record_by_student():
    repository = InMemoryStudentAcademicRecordRepository()
    record = create_record()

    repository.save(record)

    result = repository.find_by_student(record.student_id, record.tenant_id)

    assert result == record


def test_repository_returns_none_for_unknown_student():
    repository = InMemoryStudentAcademicRecordRepository()

    result = repository.find_by_student(uuid4(), uuid4())

    assert result is None


def test_repository_returns_none_for_unknown_period():
    repository = InMemoryStudentAcademicRecordRepository()
    record = create_record()

    repository.save(record)

    result = repository.find_by_student_and_period(
        record.student_id,
        uuid4(),
        record.tenant_id,
    )

    assert result is None


def test_repository_can_replace_existing_record():
    repository = InMemoryStudentAcademicRecordRepository()

    student_id = uuid4()
    academic_period_id = uuid4()
    tenant_id = uuid4()

    first_record = create_record(
        student_id=student_id,
        tenant_id=tenant_id,
        academic_period_id=academic_period_id,
        general_average=12.0,
    )

    second_record = create_record(
        student_id=student_id,
        tenant_id=tenant_id,
        academic_period_id=academic_period_id,
        general_average=16.0,
    )

    repository.save(first_record)
    repository.save(second_record)

    result = repository.find_by_student_and_period(
        student_id,
        academic_period_id,
        tenant_id,
    )

    assert result == second_record
    assert result.general_average == 16.0


def test_repository_does_not_mix_students():
    repository = InMemoryStudentAcademicRecordRepository()

    student_a = uuid4()
    student_b = uuid4()
    period = uuid4()
    tenant_id = uuid4()

    record_a = create_record(
        student_id=student_a,
        tenant_id=tenant_id,
        academic_period_id=period,
        general_average=15.0,
    )

    record_b = create_record(
        student_id=student_b,
        tenant_id=tenant_id,
        academic_period_id=period,
        general_average=10.0,
    )

    repository.save(record_a)
    repository.save(record_b)

    result_a = repository.find_by_student(student_a, tenant_id)
    result_b = repository.find_by_student(student_b, tenant_id)

    assert result_a == record_a
    assert result_b == record_b
    assert result_a != result_b

