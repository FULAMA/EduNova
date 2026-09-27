from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.subject import Subject


class SubjectRepository(ABC):

    @abstractmethod
    def save(self, subject: Subject) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(
        self,
        subject_id: UUID,
        tenant_id: UUID,
    ) -> Subject | None:
        raise NotImplementedError
