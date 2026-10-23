from abc import ABC, abstractmethod
from src.academic.domain.entities.deliberation import Deliberation


class DeliberationRepository(ABC):
    @abstractmethod
    def save(self, deliberation: Deliberation) -> Deliberation:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, deliberation_id, tenant_id):
        raise NotImplementedError

    @abstractmethod
    def validate(self, deliberation_id, tenant_id, expected_version, actor_id):
        raise NotImplementedError
