from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.subject import Subject


class SubjectRepository(ABC):

    @abstractmethod
    def save(self, subject: Subject) -> None:
        pass

    @abstractmethod
    def find_by_id(
        self,
        subject_id: UUID,
    ) -> Subject | None:
        pass
