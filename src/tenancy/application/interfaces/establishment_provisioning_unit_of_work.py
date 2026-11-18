from abc import ABC, abstractmethod

from src.identity.domain.entities.user import User
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant


class EstablishmentProvisioningConflict(Exception):
    def __init__(self, resource: str):
        self.resource = resource
        super().__init__(resource)


class EstablishmentProvisioningFailure(Exception):
    pass


class EstablishmentProvisioningUnitOfWork(ABC):
    """Application interface for atomic establishment provisioning.

    Guarantees that creating a Tenant, an administrator User, and their
    authoritative ADMIN Membership occurs within a single atomic transaction.
    If any persistence step fails (e.g. constraint violation), all changes are
    rolled back with zero orphaned records left in database.
    """

    @abstractmethod
    def provision_establishment_atomic(
        self,
        tenant: Tenant,
        user: User,
        membership: Membership,
    ) -> None:
        """Persists Tenant, User, and Membership atomically in a single transaction."""
        raise NotImplementedError
