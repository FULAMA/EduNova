from src.academic.application.dto.validate_academic_record_request import (
    ValidateAcademicRecordRequest,
)
from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)


class ValidateAcademicRecord:
    def __init__(self, repository: StudentAcademicRecordRepository):
        self._repository = repository

    def execute(self, request: ValidateAcademicRecordRequest):
        record = self._repository.find_by_student_and_period(
            request.student_id,
            request.academic_period_id,
            request.tenant_id,
        )
        if record is None:
            raise ValueError("Aucun dossier académique trouvé.")

        validated = record.validate()
        self._repository.save(
            validated,
            expected_version=request.expected_version,
            operation="VALIDATED",
        )
        return validated
