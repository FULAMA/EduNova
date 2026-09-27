from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.academic_class import AcademicClass


class AcademicClassRepository(ABC):

    @abstractmethod
    def save(self, academic_class: AcademicClass) -> None:
        pass

    @abstractmethod
    def find_by_id(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
    ) -> AcademicClass | None:
        pass
