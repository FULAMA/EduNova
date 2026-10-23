from src.academic.application.dto.create_academic_record_request import (
    CreateAcademicRecordRequest,
)
from src.academic.application.dto.create_academic_record_response import (
    CreateAcademicRecordResponse,
)
from src.academic.application.dto.subject_result_response import (
    SubjectResultResponse,
)
from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository
from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.domain.entities.student_assignment import StudentAssignmentStatus
from src.academic.domain.entities.student_academic_record import StudentAcademicRecord


class CreateAcademicRecord:
    def __init__(
        self,
        repository: StudentAcademicRecordRepository,
        *,
        assignments: StudentAssignmentRepository | None = None,
        periods: AcademicPeriodRepository | None = None,
    ):
        self._repository = repository
        self._assignments = assignments
        self._periods = periods

    def execute(
        self,
        request: CreateAcademicRecordRequest,
    ) -> CreateAcademicRecordResponse:

        if self._assignments is None or self._periods is None:
            raise RuntimeError("Les repositories d'eligibilite academique ne sont pas configures.")

        period = self._periods.find_by_id(request.academic_period_id, request.tenant_id)
        if period is None or period.academic_year_id is None:
            raise ValueError("Cette periode historique ne peut pas recevoir un nouveau dossier.")
        has_active_assignment = any(
            assignment.status is StudentAssignmentStatus.ACTIVE
            and assignment.academic_year_id == period.academic_year_id
            for assignment in self._assignments.list_by_student(request.student_id, request.tenant_id)
        )
        if not has_active_assignment:
            raise ValueError("Aucune affectation active ne correspond a cette periode.")

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

        self._repository.save(record, operation="CREATED")

        subject_results = tuple(
            SubjectResultResponse(
                subject_id=result.subject_id,
                average=result.average,
                coefficient=result.coefficient,
            )
            for result in record.subject_results
        )

        return CreateAcademicRecordResponse(
            student_id=record.student_id,
            academic_period_id=record.academic_period_id,
            subject_results=subject_results,
            general_average=record.general_average,
            failed_subjects=record.failed_subjects,
            credits_obtained=record.credits_obtained,
            total_credits=record.total_credits,
        )
