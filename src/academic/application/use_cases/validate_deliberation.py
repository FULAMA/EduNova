from uuid import UUID

from src.academic.application.exceptions import DeliberationConcurrencyError
from src.academic.application.interfaces.deliberation_repository import DeliberationRepository
from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.domain.entities.student_academic_record import AcademicRecordStatus


class ValidateDeliberation:
    def __init__(
        self,
        deliberations: DeliberationRepository,
        records: StudentAcademicRecordRepository,
    ):
        self._deliberations = deliberations
        self._records = records

    def execute(
        self,
        tenant_id: UUID,
        deliberation_id: UUID,
        expected_version: int,
        actor_id: UUID,
    ):
        deliberation = self._deliberations.find_by_id(deliberation_id, tenant_id)
        if deliberation is None:
            raise ValueError("Délibération introuvable.")
        if deliberation.status != "PREPARED":
            raise ValueError("Seule une délibération préparée peut être validée.")

        record = self._records.find_by_student_and_period(
            deliberation.student_id,
            deliberation.academic_period_id,
            tenant_id,
        )
        if record is None:
            raise ValueError("Le dossier académique source est introuvable.")
        if record.status is not AcademicRecordStatus.VALIDATED:
            raise ValueError("Le dossier académique source doit être validé.")
        if record.version != deliberation.record_version:
            raise DeliberationConcurrencyError(
                "Le dossier académique a changé depuis la préparation de la délibération."
            )
        if deliberation.version != expected_version:
            raise DeliberationConcurrencyError(
                "La délibération a changé depuis son chargement."
            )
        return self._deliberations.validate(
            deliberation_id,
            tenant_id,
            expected_version,
            actor_id,
        )
