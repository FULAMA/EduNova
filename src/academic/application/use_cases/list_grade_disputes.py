from uuid import UUID

from src.academic.application.interfaces.grade_dispute_repository import GradeDisputeRepository
from src.academic.domain.entities.grade_dispute import GradeDispute, GradeDisputeStatus


class ListGradeDisputes:
    def __init__(self, dispute_repository: GradeDisputeRepository):
        self._dispute_repository = dispute_repository

    def execute(
        self,
        tenant_id: UUID,
        *,
        student_id: UUID | None = None,
        academic_period_id: UUID | None = None,
        subject_id: UUID | None = None,
        status: GradeDisputeStatus | None = None,
    ) -> tuple[GradeDispute, ...]:
        return self._dispute_repository.list(
            tenant_id,
            student_id=student_id,
            academic_period_id=academic_period_id,
            subject_id=subject_id,
            status=status,
        )
