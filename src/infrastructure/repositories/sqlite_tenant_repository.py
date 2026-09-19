from uuid import UUID

from src.application.interfaces.tenant_repository import TenantRepository
from src.domain.entities.tenant import Tenant
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteTenantRepository(TenantRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def find_by_id(self, tenant_id: UUID) -> Tenant | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT id, name, slug, active FROM tenants WHERE id = ?",
                (str(tenant_id),),
            ).fetchone()
        if row is None:
            return None
        return Tenant(UUID(row["id"]), row["name"], row["slug"], bool(row["active"]))
