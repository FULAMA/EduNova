from src.application.dto.create_academic_record_request import (
    CreateAcademicRecordRequest,
)
from src.application.dto.create_academic_record_response import (
    CreateAcademicRecordResponse,
)
from src.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.domain.entities.student_academic_record import StudentAcademicRecord


class CreateAcademicRecord:
    def __init__(
        self,
        repository: StudentAcademicRecordRepository,
    ):
        self._repository = repository

    def execute(
        self,
        request: CreateAcademicRecordRequest,
    ) -> CreateAcademicRecordResponse:

        existing_record = self._repository.find_by_student_and_period(
            request.student_id,
            request.academic_period_id,
            request.tenant_id,
        )

        if existing_record is not None:
            raise ValueError(
                "Academic record already exists"
            )

        record = StudentAcademicRecord(
            tenant_id=request.tenant_id,
            student_id=request.student_id,
            academic_period_id=request.academic_period_id,
            subject_results=(),
            general_average=0,
            failed_subjects=0,
            credits_obtained=0,
            total_credits=request.total_credits,
        )

        self._repository.save(record)

        return CreateAcademicRecordResponse(
            student_id=record.student_id,
            academic_period_id=record.academic_period_id,
            subject_results=record.subject_results,
            general_average=record.general_average,
            failed_subjects=record.failed_subjects,
            credits_obtained=record.credits_obtained,
            total_credits=record.total_credits,
        )