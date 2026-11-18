from uuid import UUID

from src.academic.application.interfaces.grade_dispute_repository import GradeDisputeRepository
from src.academic.domain.entities.grade_dispute import GradeDispute


class ReviewGradeDispute:
    def __init__(self, dispute_repository: GradeDisputeRepository):
        self._dispute_repository = dispute_repository

    def execute(
        self,
        tenant_id: UUID,
        dispute_id: UUID,
        reviewer_id: UUID,
    ) -> GradeDispute:
        dispute = self._dispute_repository.find_by_id(dispute_id, tenant_id)
        if dispute is None:
            raise LookupError("Contestation introuvable dans cet etablissement.")

        updated = dispute.start_review(reviewer_id)
        self._dispute_repository.save(updated)
        return updated
