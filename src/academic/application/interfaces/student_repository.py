from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.domain.entities.student import Student


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

    @abstractmethod
    def find_by_registration_number(
        self,
        tenant_id: UUID,
        registration_number: str,
    ) -> StudentSummary | None:
        raise NotImplementedError

    @abstractmethod
    def find_potential_duplicates(
        self,
        tenant_id: UUID,
        first_name: str,
        last_name: str,
        exclude_id: UUID | None = None,
    ) -> tuple[StudentSummary, ...]:
        raise NotImplementedError

    @abstractmethod
    def save(self, student: Student) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, student: Student) -> None:
        raise NotImplementedError
