from abc import ABC, abstractmethod
from uuid import UUID

from src.identity.domain.entities.external_identity import ExternalIdentity


class ExternalIdentityRepository(ABC):
    @abstractmethod
    def find_by_provider_and_subject(
        self,
        provider: str,
        subject: str,
    ) -> ExternalIdentity | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_user_and_provider(
        self,
        user_id: UUID,
        provider: str,
    ) -> ExternalIdentity | None:
        raise NotImplementedError

    @abstractmethod
    def link(self, identity: ExternalIdentity) -> ExternalIdentity:
        raise NotImplementedError
