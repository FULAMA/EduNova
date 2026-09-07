from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.membership import Membership


class MembershipRepository(ABC):

    @abstractmethod
    def save(self, membership: Membership) -> None:
        pass

    @abstractmethod
    def find_by_id(self, membership_id: UUID) -> Membership | None:
        pass

    @abstractmethod
    def find_by_user(self, user_id: UUID) -> list[Membership]:
        pass

    @abstractmethod
    def find_by_user_and_tenant(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> Membership | None:
        pass
