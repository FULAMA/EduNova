from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.academic_option import AcademicOption


class AcademicOptionRepository(ABC):

    @abstractmethod
    def save(
        self,
        academic_option: AcademicOption,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(
        self,
        academic_option_id: UUID,
        tenant_id: UUID,
    ) -> AcademicOption | None:
        raise NotImplementedError
