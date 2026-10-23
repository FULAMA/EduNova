from src.academic.application.dto.analyze_student_academic_record_request import (
    AnalyzeStudentAcademicRecordRequest,
)
from src.academic.application.dto.analyze_student_academic_record_response import (
    AnalyzeStudentAcademicRecordResponse,
)
from src.academic.application.dto.subject_result_response import (
    SubjectResultResponse,
)
from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository


class AnalyzeStudentAcademicRecord:
    def __init__(
        self,
        repository: StudentAcademicRecordRepository,
        subject_repository: SubjectRepository | None = None,
        period_repository: AcademicPeriodRepository | None = None,
    ):
        self._repository = repository
        self._subject_repository = subject_repository
        self._period_repository = period_repository

    def execute(
        self,
        request: AnalyzeStudentAcademicRecordRequest,
    ) -> AnalyzeStudentAcademicRecordResponse:

        record = self._repository.find_by_student_and_period(
            request.student_id,
            request.academic_period_id,
            request.tenant_id,
        )

        if record is None:
            raise ValueError(
                "Aucun dossier académique trouvé pour "
                "cet étudiant et cette période."
            )

        subject_results = tuple(
            SubjectResultResponse(
                subject_id=result.subject_id,
                average=result.average,
                coefficient=result.coefficient,
            )
            for result in record.subject_results
        )

        subject_names = None
        if self._subject_repository is not None:
            subjects = self._subject_repository.find_many_by_ids(
                {result.subject_id for result in subject_results}, request.tenant_id
            )
            subject_names = {subject_id: subject.name for subject_id, subject in subjects.items()}
        period = (
            self._period_repository.find_by_id(record.academic_period_id, request.tenant_id)
            if self._period_repository is not None else None
        )

        return AnalyzeStudentAcademicRecordResponse(
            student_id=record.student_id,
            academic_period_id=record.academic_period_id,
            general_average=record.general_average,
            failed_subjects=record.failed_subjects,
            credits_obtained=record.credits_obtained,
            total_credits=record.total_credits,
            subject_results=subject_results,
            status=record.status.value,
            version=record.version,
            subject_names=subject_names,
            academic_period_name=period.name if period is not None else None,
        )
