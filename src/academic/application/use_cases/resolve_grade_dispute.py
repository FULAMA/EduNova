from uuid import UUID

from src.academic.application.interfaces.grade_dispute_repository import GradeDisputeRepository
from src.academic.domain.entities.grade_dispute import GradeDispute, GradeDisputeStatus


class ResolveGradeDispute:
    def __init__(self, dispute_repository: GradeDisputeRepository):
        self._dispute_repository = dispute_repository

    def execute(
        self,
        tenant_id: UUID,
        dispute_id: UUID,
        decision: GradeDisputeStatus,
        resolution_notes: str,
        reviewer_id: UUID,
    ) -> GradeDispute:
        dispute = self._dispute_repository.find_by_id(dispute_id, tenant_id)
        if dispute is None:
            raise LookupError("Contestation introuvable dans cet etablissement.")

        updated = dispute.resolve(
            decision=decision,
            resolution_notes=resolution_notes,
            reviewer_id=reviewer_id,
        )
        self._dispute_repository.save(updated)
        return updated
