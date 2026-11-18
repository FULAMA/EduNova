import sqlite3
from uuid import UUID

from src.infrastructure.persistence.database import SQLiteDatabase
from src.tenancy.application.interfaces.tenant_repository import TenantRepository
from src.tenancy.domain.entities.tenant import Tenant


class SQLiteTenantRepository(TenantRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(
        self,
        tenant: Tenant,
        connection: sqlite3.Connection | None = None,
    ) -> None:
        query = (
            "INSERT INTO tenants (id, name, slug, active) "
            "VALUES (?, ?, ?, ?)"
        )
        params = (
            str(tenant.id),
            tenant.name,
            tenant.slug,
            int(tenant.active),
        )

        if connection is not None:
            connection.execute(query, params)
            return

        with self._database.connect() as conn:
            conn.execute(query, params)

    def find_by_id(
        self,
        tenant_id: UUID,
        connection: sqlite3.Connection | None = None,
    ) -> Tenant | None:
        query = "SELECT id, name, slug, active FROM tenants WHERE id = ?"
        params = (str(tenant_id),)

        if connection is not None:
            row = connection.execute(query, params).fetchone()
        else:
            with self._database.connect() as conn:
                row = conn.execute(query, params).fetchone()

        if row is None:
            return None
        return Tenant(UUID(row["id"]), row["name"], row["slug"], bool(row["active"]))

    def find_by_slug(
        self,
        slug: str,
        connection: sqlite3.Connection | None = None,
    ) -> Tenant | None:
        normalized_slug = slug.strip().lower()
        query = "SELECT id, name, slug, active FROM tenants WHERE LOWER(slug) = ?"
        params = (normalized_slug,)

        if connection is not None:
            row = connection.execute(query, params).fetchone()
        else:
            with self._database.connect() as conn:
                row = conn.execute(query, params).fetchone()

        if row is None:
            return None
        return Tenant(UUID(row["id"]), row["name"], row["slug"], bool(row["active"]))
