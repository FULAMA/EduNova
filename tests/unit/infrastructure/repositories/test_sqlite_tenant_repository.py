from uuid import uuid4

from src.infrastructure.persistence.database import SQLiteDatabase
from src.tenancy.domain.entities.tenant import Tenant
from src.tenancy.infrastructure.repositories.sqlite_tenant_repository import (
    SQLiteTenantRepository,
)


def create_tenants_table(database: SQLiteDatabase) -> None:
    with database.connect() as connection:
        connection.execute(
            """
            CREATE TABLE tenants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                active INTEGER NOT NULL
            )
            """
        )


def test_find_by_id_returns_tenant(tmp_path):
    database = SQLiteDatabase(str(tmp_path / "test.db"))
    create_tenants_table(database)

    tenant_id = uuid4()

    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO tenants (id, name, slug, active)
            VALUES (?, ?, ?, ?)
            """,
            (str(tenant_id), "Bonsomi", "bonsomi", 1),
        )

    repository = SQLiteTenantRepository(database)

    result = repository.find_by_id(tenant_id)

    assert isinstance(result, Tenant)
    assert result.id == tenant_id
    assert result.name == "Bonsomi"
    assert result.slug == "bonsomi"
    assert result.active is True


def test_find_by_id_returns_none_when_tenant_does_not_exist(tmp_path):
    database = SQLiteDatabase(str(tmp_path / "test.db"))
    create_tenants_table(database)

    repository = SQLiteTenantRepository(database)

    result = repository.find_by_id(uuid4())

    assert result is None
