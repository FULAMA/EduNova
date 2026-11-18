import sqlite3

from src.identity.domain.entities.user import User
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
from src.tenancy.application.interfaces.establishment_provisioning_unit_of_work import (
    EstablishmentProvisioningConflict,
    EstablishmentProvisioningFailure,
    EstablishmentProvisioningUnitOfWork,
)
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant
from src.tenancy.infrastructure.repositories.sqlite_membership_repository import (
    SQLiteMembershipRepository,
)
from src.tenancy.infrastructure.repositories.sqlite_tenant_repository import (
    SQLiteTenantRepository,
)


class SQLiteEstablishmentProvisioningUnitOfWork(EstablishmentProvisioningUnitOfWork):
    """SQLite implementation of the atomic establishment provisioning unit of work.

    Executes Tenant, User, and Membership persistence within a single SQLite
    connection transaction (with connection:). Any IntegrityError or operational
    failure triggers an automatic rollback of all modified tables.
    """

    def __init__(
        self,
        database: SQLiteDatabase,
        tenant_repository: SQLiteTenantRepository,
        user_repository: SQLiteUserRepository,
        membership_repository: SQLiteMembershipRepository,
    ):
        self._database = database
        self._tenant_repo = tenant_repository
        self._user_repo = user_repository
        self._membership_repo = membership_repository

    def provision_establishment_atomic(
        self,
        tenant: Tenant,
        user: User,
        membership: Membership,
    ) -> None:
        """Persists Tenant, User, and Membership inside a single atomic transaction."""
        try:
            with self._database.connect() as connection:
                with connection:
                    self._tenant_repo.save(tenant, connection=connection)
                    self._user_repo.save(user, connection=connection)
                    self._membership_repo.save(membership, connection=connection)
        except sqlite3.IntegrityError as exc:
            message = str(exc)
            if "users.email" in message:
                raise EstablishmentProvisioningConflict("email") from exc
            if "tenants.slug" in message:
                raise EstablishmentProvisioningConflict("slug") from exc
            raise EstablishmentProvisioningConflict("integrity") from exc
        except sqlite3.Error as exc:
            raise EstablishmentProvisioningFailure() from exc


