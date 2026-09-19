from uuid import uuid4

from src.application.dto.analyze_student_academic_record_request import (
    AnalyzeStudentAcademicRecordRequest,
)
from src.application.dto.analyze_student_academic_record_response import (
    AnalyzeStudentAcademicRecordResponse,
)
from src.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.domain.entities.student_academic_record import StudentAcademicRecord
from src.domain.value_objects.subject_result import SubjectResult
from tests.support.tenant import TEST_TENANT_ID


class FakeStudentAcademicRecordRepository(StudentAcademicRecordRepository):
    def __init__(self, record=None):
        self.record = record

    def save(self, record: StudentAcademicRecord) -> None:
        self.record = record

    def find_by_student(self, student_id):
        if self.record and self.record.student_id == student_id:
            return self.record

        return None

    def find_by_student_and_period(
        self,
        student_id,
        academic_period_id,
        tenant_id,
    ):
        if (
            self.record
            and self.record.tenant_id == tenant_id
            and self.record.student_id == student_id
            and self.record.academic_period_id == academic_period_id
        ):
            return self.record

        return None


def create_record():
    return StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
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
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )


def test_use_case_depends_only_on_repository_interface():
    record = create_record()

    repository = FakeStudentAcademicRecordRepository(record)

    use_case = AnalyzeStudentAcademicRecord(repository)

    request = AnalyzeStudentAcademicRecordRequest(
        tenant_id=record.tenant_id,
        student_id=record.student_id,
        academic_period_id=record.academic_period_id,
    )

    response = use_case.execute(request)

    assert isinstance(
        response,
        AnalyzeStudentAcademicRecordResponse,
    )

    assert response.student_id == record.student_id
    assert response.academic_period_id == record.academic_period_id
    assert response.general_average == 15.0


def test_fake_repository_proves_infrastructure_is_not_required():
    record = create_record()

    repository = FakeStudentAcademicRecordRepository(record)

    use_case = AnalyzeStudentAcademicRecord(repository)

    request = AnalyzeStudentAcademicRecordRequest(
        tenant_id=record.tenant_id,
        student_id=record.student_id,
        academic_period_id=record.academic_period_id,
    )

    response = use_case.execute(request)

    assert response.general_average == record.general_average
