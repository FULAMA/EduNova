from src.academic.application.dto.correct_academic_record_request import (
    CorrectAcademicRecordRequest,
)
from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.domain.policies.academic_policy import AcademicPolicy
from src.academic.domain.services.academic_average_calculator import (
    AcademicAverageCalculator,
)


class CorrectAcademicRecord:
    def __init__(self, repository: StudentAcademicRecordRepository):
        self._repository = repository
        self._policy = AcademicPolicy()
        self._average_calculator = AcademicAverageCalculator()

    def execute(self, request: CorrectAcademicRecordRequest):
        reason = request.reason.strip()
        if not reason:
            raise ValueError("Le motif de correction est obligatoire.")

        record = self._repository.find_by_student_and_period(
            request.student_id,
            request.academic_period_id,
            request.tenant_id,
        )
        if record is None:
            raise ValueError("Aucun dossier académique trouvé.")

        if record.subject_results:
            general_average, failed_subjects = record.calculate_aggregates(
                record.subject_results,
                policy=self._policy,
                average_calculator=self._average_calculator,
            )
        else:
            # Empty-record validation remains unchanged until completeness is
            # decided. Client-provided aggregate values are never authoritative.
            general_average = record.general_average
            failed_subjects = record.failed_subjects

        corrected = record.create_new_version(
            general_average=general_average,
            failed_subjects=failed_subjects,
            credits_obtained=record.credits_obtained,
        )
        self._repository.save(
            corrected,
            expected_version=request.expected_version,
            operation="CORRECTED",
            actor_id=request.actor_id,
            reason=reason,
        )
        return corrected
