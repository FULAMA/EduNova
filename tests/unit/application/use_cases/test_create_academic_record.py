from uuid import uuid4

import pytest

from src.application.dto.create_academic_record_request import (
    CreateAcademicRecordRequest,
)
from src.application.use_cases.create_academic_record import (
    CreateAcademicRecord,
)
from src.infrastructure.repositories.in_memory_student_academic_record_repository import (
    InMemoryStudentAcademicRecordRepository,
)


def test_create_academic_record_creates_empty_record():
    repository = InMemoryStudentAcademicRecordRepository()
    use_case = CreateAcademicRecord(repository)

    student_id = uuid4()
    academic_period_id = uuid4()

    request = CreateAcademicRecordRequest(
        student_id=student_id,
        academic_period_id=academic_period_id,
        total_credits=30,
    )

    use_case.execute(request)

    record = repository.find_by_student_and_period(
        student_id,
        academic_period_id,
    )

    assert record is not None
    assert record.student_id == student_id
    assert record.academic_period_id == academic_period_id
    assert record.subject_results == ()
    assert record.general_average == 0
    assert record.failed_subjects == 0
    assert record.credits_obtained == 0
    assert record.total_credits == 30


def test_create_academic_record_rejects_duplicate():
    repository = InMemoryStudentAcademicRecordRepository()
    use_case = CreateAcademicRecord(repository)

    student_id = uuid4()
    academic_period_id = uuid4()

    request = CreateAcademicRecordRequest(
        student_id=student_id,
        academic_period_id=academic_period_id,
        total_credits=30,
    )

    use_case.execute(request)

    with pytest.raises(ValueError, match="Academic record already exists"):
        use_case.execute(request)
from uuid import uuid4

from src.application.dto.create_academic_record_request import (
    CreateAcademicRecordRequest,
)
from src.application.use_cases.create_academic_record import (
    CreateAcademicRecord,
)
from src.infrastructure.repositories.in_memory_student_academic_record_repository import (
    InMemoryStudentAcademicRecordRepository,
)


def test_create_academic_record_returns_created_record():
    repository = InMemoryStudentAcademicRecordRepository()
    use_case = CreateAcademicRecord(repository)

    student_id = uuid4()
    academic_period_id = uuid4()

    request = CreateAcademicRecordRequest(
        student_id=student_id,
        academic_period_id=academic_period_id,
        total_credits=30,
    )

    response = use_case.execute(request)

    assert response.student_id == student_id
    assert response.academic_period_id == academic_period_id
    assert response.subject_results == ()
    assert response.general_average == 0
    assert response.failed_subjects == 0
    assert response.credits_obtained == 0
    assert response.total_credits == 30
