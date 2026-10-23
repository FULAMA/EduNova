from abc import ABC, abstractmethod
from uuid import UUID

from src.identity.domain.entities.student_user_link import StudentUserLink


class StudentUserLinkRepository(ABC):
    @abstractmethod
    def save(self, link: StudentUserLink) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_user(self, user_id: UUID, tenant_id: UUID) -> tuple[StudentUserLink, ...]:
        raise NotImplementedError

