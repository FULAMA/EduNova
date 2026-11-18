from abc import ABC, abstractmethod
from uuid import UUID

from src.identity.domain.entities.parent_student_link import ParentStudentLink


class ParentStudentLinkRepository(ABC):
    @abstractmethod
    def save(self, link: ParentStudentLink) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_by_parent(self, tenant_id: UUID, parent_user_id: UUID) -> tuple[ParentStudentLink, ...]:
        raise NotImplementedError

    @abstractmethod
    def list_by_student(self, tenant_id: UUID, student_id: UUID) -> tuple[ParentStudentLink, ...]:
        raise NotImplementedError

    @abstractmethod
    def is_parent_of(self, tenant_id: UUID, parent_user_id: UUID, student_id: UUID) -> bool:
        raise NotImplementedError
