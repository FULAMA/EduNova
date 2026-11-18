from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.grade_dispute import GradeDispute, GradeDisputeStatus


class GradeDisputeRepository(ABC):
    @abstractmethod
    def student_is_active_in_tenant(self, student_id: UUID, tenant_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def academic_period_exists_in_tenant(self, period_id: UUID, tenant_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def subject_exists_in_tenant(self, subject_id: UUID, tenant_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def save(self, dispute: GradeDispute) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, dispute_id: UUID, tenant_id: UUID) -> GradeDispute | None:
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        tenant_id: UUID,
        *,
        student_id: UUID | None = None,
        academic_period_id: UUID | None = None,
        subject_id: UUID | None = None,
        status: GradeDisputeStatus | None = None,
    ) -> tuple[GradeDispute, ...]:
        raise NotImplementedError
