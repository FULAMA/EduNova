from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.class_option import ClassOption


class ClassOptionRepository(ABC):

    @abstractmethod
    def save(self, class_option: ClassOption) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(
        self,
        class_option_id: UUID,
        tenant_id: UUID,
    ) -> ClassOption | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_class_and_option(
        self,
        academic_class_id: UUID,
        academic_option_id: UUID,
        tenant_id: UUID,
    ) -> ClassOption | None:
        raise NotImplementedError