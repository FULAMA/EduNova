from uuid import UUID

from src.academic.application.interfaces.grade_dispute_repository import GradeDisputeRepository
from src.academic.domain.entities.grade_dispute import GradeDispute


class SubmitGradeDispute:
    def __init__(
        self,
        dispute_repository: GradeDisputeRepository,
    ):
        self._dispute_repository = dispute_repository

    def execute(
        self,
        tenant_id: UUID,
        student_id: UUID,
        academic_period_id: UUID,
        subject_id: UUID,
        reason: str,
        submitted_by: UUID,
    ) -> GradeDispute:
        if not self._dispute_repository.student_is_active_in_tenant(student_id, tenant_id):
            raise LookupError("Eleve actif introuvable dans cet etablissement.")
        if not self._dispute_repository.academic_period_exists_in_tenant(
            academic_period_id, tenant_id
        ):
            raise LookupError("Periode scolaire introuvable dans cet etablissement.")
        if not self._dispute_repository.subject_exists_in_tenant(subject_id, tenant_id):
            raise LookupError("Matiere introuvable dans cet etablissement.")

        dispute = GradeDispute.create(
            tenant_id=tenant_id,
            student_id=student_id,
            academic_period_id=academic_period_id,
            subject_id=subject_id,
            reason=reason,
            submitted_by=submitted_by,
        )
        self._dispute_repository.save(dispute)
        return dispute
