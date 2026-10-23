from uuid import UUID

from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.domain.entities.deliberation import Deliberation
from src.academic.domain.entities.student_academic_record import AcademicRecordStatus
from src.academic.domain.services.deliberation_engine import DeliberationEngine
from src.academic.domain.policies.academic_policy import AcademicPolicy
from src.academic.domain.services.academic_average_calculator import (
    AcademicAverageCalculator,
)


class PrepareDeliberation:
    """Compute a decision from one validated, tenant-scoped record.

    Persistence of a separately validated deliberation is intentionally not
    introduced until its lifecycle and audit contract are approved.
    """

    def __init__(
        self,
        records: StudentAcademicRecordRepository,
        policy: AcademicPolicy | None = None,
        deliberations=None,
    ):
        self._records = records
        self._engine = DeliberationEngine(policy or AcademicPolicy())
        self._deliberations = deliberations

    def execute(
        self, tenant_id: UUID, student_id: UUID, academic_period_id: UUID, actor_id: UUID | None = None
    ) -> Deliberation:
        record = self._records.find_by_student_and_period(
            student_id, academic_period_id, tenant_id
        )
        if record is None:
            raise ValueError("Aucun dossier academique trouve pour cette periode.")
        if record.status is not AcademicRecordStatus.VALIDATED:
            raise ValueError("La deliberation exige un dossier academique valide.")

        if record.subject_results:
            average, failed_subjects = record.calculate_aggregates(
                record.subject_results,
                policy=self._engine.policy,
                average_calculator=AcademicAverageCalculator(),
            )
        else:
            average = record.general_average
            failed_subjects = record.failed_subjects

        result = self._engine.deliberate(
            student_id=record.student_id,
            average=average,
            failed_subjects=failed_subjects,
        )
        deliberation = Deliberation(
            student_id=result.student_id,
            average=result.average,
            failed_subjects=result.failed_subjects,
            decision=result.decision,
            tenant_id=tenant_id,
            academic_period_id=academic_period_id,
            record_version=record.version,
            created_by=actor_id,
        )
        if self._deliberations is not None:
            return self._deliberations.save(deliberation)
        return deliberation
