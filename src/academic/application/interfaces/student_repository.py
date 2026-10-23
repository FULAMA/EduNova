from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.application.dto.student_summary import StudentSummary


class StudentRepository(ABC):
    @abstractmethod
    def list_by_tenant(self, tenant_id: UUID) -> tuple[StudentSummary, ...]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id_and_tenant(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> StudentSummary | None:
        raise NotImplementedError
