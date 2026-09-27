from src.academic.application.dto.add_subject_result_request import (
    AddSubjectResultRequest,
)
from src.academic.application.dto.add_subject_result_response import (
    AddSubjectResultResponse,
)
from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.domain.value_objects.subject_result import SubjectResult


class AddSubjectResult:
    def __init__(
        self,
        repository: StudentAcademicRecordRepository,
    ):
        self._repository = repository

    def execute(
        self,
        request: AddSubjectResultRequest,
    ) -> AddSubjectResultResponse:

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

        subject_result = SubjectResult(
            subject_id=request.subject_id,
            average=request.average,
            coefficient=request.coefficient,
        )

        updated_record = record.with_subject_result(
            subject_result
        )

        self._repository.save(updated_record)

        return AddSubjectResultResponse(
            subject_id=subject_result.subject_id,
            average=subject_result.average,
            coefficient=subject_result.coefficient,
        )
