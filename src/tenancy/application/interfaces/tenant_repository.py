from abc import ABC, abstractmethod
from uuid import UUID

from src.tenancy.domain.entities.tenant import Tenant


class TenantRepository(ABC):
    @abstractmethod
    def save(self, tenant: Tenant) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, tenant_id: UUID) -> Tenant | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_slug(self, slug: str) -> Tenant | None:
        raise NotImplementedError
