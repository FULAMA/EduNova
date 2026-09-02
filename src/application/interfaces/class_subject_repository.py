from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.class_subject import ClassSubject


class ClassSubjectRepository(ABC):

    @abstractmethod
    def save(self, class_subject: ClassSubject) -> None:
        pass

    @abstractmethod
    def find_by_id(
        self,
        class_subject_id: UUID,
    ) -> ClassSubject | None:
        pass

    @abstractmethod
    def find_by_class(
        self,
        academic_class_id: UUID,
    ) -> list[ClassSubject]:
        pass

    @abstractmethod
    def find_by_class_and_option(
        self,
        academic_class_id: UUID,
        academic_option_id: UUID | None,
    ) -> list[ClassSubject]:
        pass
