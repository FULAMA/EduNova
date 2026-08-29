from uuid import uuid4

from src.application.dto.analyze_student_academic_record_request import (
    AnalyzeStudentAcademicRecordRequest,
)
from src.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.domain.entities.student_academic_record import StudentAcademicRecord
from src.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.repositories.in_memory_student_academic_record_repository import (
    InMemoryStudentAcademicRecordRepository,
)


def create_record(
    student_id=None,
    academic_period_id=None,
    average=14.0,
):
    return StudentAcademicRecord(
        student_id=student_id or uuid4(),
        academic_period_id=academic_period_id or uuid4(),
        subject_results=(
            SubjectResult(
                subject_id=uuid4(),
                average=average,
                coefficient=2.0,
            ),
        ),
        general_average=average,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )


def test_use_case_can_analyze_existing_student_record():
    repository = InMemoryStudentAcademicRecordRepository()

    student_id = uuid4()
    period_id = uuid4()

    record = create_record(
        student_id=student_id,
        academic_period_id=period_id,
        average=14.0,
    )

    repository.save(record)

    use_case = AnalyzeStudentAcademicRecord(repository)

    request = AnalyzeStudentAcademicRecordRequest(
        student_id=student_id,
        academic_period_id=period_id,
    )

    response = use_case.execute(request)

    assert response.student_id == student_id
    assert response.academic_period_id == period_id
    assert response.general_average == 14.0


def test_use_case_raises_error_when_record_does_not_exist():
    repository = InMemoryStudentAcademicRecordRepository()

    use_case = AnalyzeStudentAcademicRecord(repository)

    request = AnalyzeStudentAcademicRecordRequest(
        student_id=uuid4(),
        academic_period_id=uuid4(),
    )

    try:
        use_case.execute(request)
        assert False, "Une exception était attendue."
    except ValueError as error:
        assert "dossier académique" in str(error).lower()


def test_use_case_uses_the_requested_student_and_period():
    repository = InMemoryStudentAcademicRecordRepository()

    student_id = uuid4()
    period_id = uuid4()

    record = create_record(
        student_id=student_id,
        academic_period_id=period_id,
    )

    repository.save(record)

    use_case = AnalyzeStudentAcademicRecord(repository)

    request = AnalyzeStudentAcademicRecordRequest(
        student_id=student_id,
        academic_period_id=period_id,
    )

    response = use_case.execute(request)

    assert response.student_id == student_id
    assert response.academic_period_id == period_id


def test_use_case_does_not_return_record_from_another_period():
    repository = InMemoryStudentAcademicRecordRepository()

    student_id = uuid4()

    record = create_record(
        student_id=student_id,
        academic_period_id=uuid4(),
    )

    repository.save(record)

    use_case = AnalyzeStudentAcademicRecord(repository)

    request = AnalyzeStudentAcademicRecordRequest(
        student_id=student_id,
        academic_period_id=uuid4(),
    )

    try:
        use_case.execute(request)
        assert False, "Une exception était attendue."
    except ValueError:
        pass
