from src.application.dto.add_subject_result_request import (
    AddSubjectResultRequest,
)
from src.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.domain.value_objects.subject_result import SubjectResult


class AddSubjectResult:
    def __init__(
        self,
        repository: StudentAcademicRecordRepository,
    ):
        self._repository = repository

    def execute(
        self,
        request: AddSubjectResultRequest,
    ) -> SubjectResult:

        record = self._repository.find_by_student_and_period(
            request.student_id,
            request.academic_period_id,
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

        return subject_result
