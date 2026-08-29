from src.application.dto.analyze_student_academic_record_request import (
    AnalyzeStudentAcademicRecordRequest,
)
from src.application.dto.analyze_student_academic_record_response import (
    AnalyzeStudentAcademicRecordResponse,
)
from src.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)


class AnalyzeStudentAcademicRecord:
    def __init__(
        self,
        repository: StudentAcademicRecordRepository,
    ):
        self._repository = repository

    def execute(
        self,
        request: AnalyzeStudentAcademicRecordRequest,
    ) -> AnalyzeStudentAcademicRecordResponse:

        record = self._repository.find_by_student_and_period(
            request.student_id,
            request.academic_period_id,
        )

        if record is None:
            raise ValueError(
                "Aucun dossier académique trouvé pour "
                "cet étudiant et cette période."
            )

        return AnalyzeStudentAcademicRecordResponse(
            student_id=record.student_id,
            academic_period_id=record.academic_period_id,
            general_average=record.general_average,
            failed_subjects=record.failed_subjects,
            credits_obtained=record.credits_obtained,
            total_credits=record.total_credits,
            subject_results=record.subject_results,
        )
