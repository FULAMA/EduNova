from uuid import uuid4
from datetime import date
from types import SimpleNamespace

import pytest

from src.academic.application.dto.create_academic_record_request import (
    CreateAcademicRecordRequest,
)
from src.academic.application.use_cases.create_academic_record import (
    CreateAcademicRecord,
)
from src.infrastructure.repositories.in_memory_student_academic_record_repository import (
    InMemoryStudentAcademicRecordRepository,
)
from src.academic.domain.entities.student_assignment import StudentAssignmentStatus


class FakeAssignments:
    def __init__(self, student_id, tenant_id, year_id):
        self.item = SimpleNamespace(student_id=student_id, tenant_id=tenant_id,
                                    academic_year_id=year_id, status=StudentAssignmentStatus.ACTIVE)
    def list_by_student(self, student_id, tenant_id):
        return (self.item,) if (student_id, tenant_id) == (self.item.student_id, self.item.tenant_id) else ()


class FakePeriods:
    def __init__(self, period): self.period = period
    def find_by_id(self, period_id, tenant_id):
        return self.period if (period_id, tenant_id) == (self.period.id, self.period.tenant_id) else None


def make_use_case(repository, student_id, tenant_id, period_id):
    from src.academic.domain.entities.academic_period import AcademicPeriod
    year_id = uuid4()
    period = AcademicPeriod(period_id, tenant_id, "Trimestre 1", date(2026, 9, 1), date(2026, 12, 20), year_id)
    return CreateAcademicRecord(repository, assignments=FakeAssignments(student_id, tenant_id, year_id), periods=FakePeriods(period))


def test_create_academic_record_creates_empty_record():
    repository = InMemoryStudentAcademicRecordRepository()
    tenant_id = uuid4()
    student_id = uuid4()
    academic_period_id = uuid4()
    use_case = make_use_case(repository, student_id, tenant_id, academic_period_id)

    request = CreateAcademicRecordRequest(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=academic_period_id,
        total_credits=30,
    )

    use_case.execute(request)

    record = repository.find_by_student_and_period(
        student_id,
        academic_period_id,
        tenant_id,
    )

    assert record is not None
    assert record.tenant_id == tenant_id
    assert record.student_id == student_id
    assert record.academic_period_id == academic_period_id
    assert record.subject_results == ()
    assert record.general_average == 0
    assert record.failed_subjects == 0
    assert record.credits_obtained == 0
    assert record.total_credits == 30


def test_create_academic_record_rejects_duplicate():
    repository = InMemoryStudentAcademicRecordRepository()
    tenant_id = uuid4()
    student_id = uuid4()
    academic_period_id = uuid4()
    use_case = make_use_case(repository, student_id, tenant_id, academic_period_id)

    request = CreateAcademicRecordRequest(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=academic_period_id,
        total_credits=30,
    )

    use_case.execute(request)

    with pytest.raises(ValueError, match="Academic record already exists"):
        use_case.execute(request)
