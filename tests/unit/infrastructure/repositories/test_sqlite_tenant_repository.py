import sqlite3
from uuid import uuid4

import pytest

from src.infrastructure.persistence.database import SQLiteDatabase
from src.tenancy.domain.entities.tenant import Tenant
from src.tenancy.infrastructure.repositories.sqlite_tenant_repository import (
    SQLiteTenantRepository,
)


def create_tenants_table(database: SQLiteDatabase) -> None:
    with database.connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                active INTEGER NOT NULL
            )
            """
        )


def test_save_and_find_by_id(tmp_path):
    database = SQLiteDatabase(str(tmp_path / "test.db"))
    create_tenants_table(database)
    repository = SQLiteTenantRepository(database)

    tenant = Tenant(
        id=uuid4(),
        name="Complexe Scolaire Cardinal Malula",
        slug="cs-cardinal-malula",
        active=True,
    )
    repository.save(tenant)

    retrieved = repository.find_by_id(tenant.id)
    assert retrieved is not None
    assert retrieved.id == tenant.id
    assert retrieved.name == tenant.name
    assert retrieved.slug == "cs-cardinal-malula"
    assert retrieved.active is True


def test_find_by_id_returns_none_when_not_found(tmp_path):
    database = SQLiteDatabase(str(tmp_path / "test.db"))
    create_tenants_table(database)
    repository = SQLiteTenantRepository(database)

    assert repository.find_by_id(uuid4()) is None


def test_find_by_slug(tmp_path):
    database = SQLiteDatabase(str(tmp_path / "test.db"))
    create_tenants_table(database)
    repository = SQLiteTenantRepository(database)

    tenant = Tenant(
        id=uuid4(),
        name="Institut Lumumba",
        slug="institut-lumumba",
        active=True,
    )
    repository.save(tenant)

    # Exact match
    retrieved = repository.find_by_slug("institut-lumumba")
    assert retrieved is not None
    assert retrieved.id == tenant.id
    assert retrieved.slug == "institut-lumumba"

    # Case-insensitive / whitespace-tolerant lookup
    retrieved_case = repository.find_by_slug("  INSTITUT-LUMUMBA  ")
    assert retrieved_case is not None
    assert retrieved_case.id == tenant.id


def test_find_by_slug_returns_none_when_not_found(tmp_path):
    database = SQLiteDatabase(str(tmp_path / "test.db"))
    create_tenants_table(database)
    repository = SQLiteTenantRepository(database)

    assert repository.find_by_slug("unknown-school") is None


def test_duplicate_slug_raises_integrity_error(tmp_path):
    database = SQLiteDatabase(str(tmp_path / "test.db"))
    create_tenants_table(database)
    repository = SQLiteTenantRepository(database)

    tenant1 = Tenant(
        id=uuid4(),
        name="Lycée Motema Mpiko",
        slug="motema-mpiko",
        active=True,
    )
    repository.save(tenant1)

    tenant2 = Tenant(
        id=uuid4(),
        name="Autre Lycée Motema Mpiko",
        slug="motema-mpiko",  # Same slug
        active=True,
    )
    with pytest.raises(sqlite3.IntegrityError):
        repository.save(tenant2)


def test_duplicate_id_raises_integrity_error(tmp_path):
    database = SQLiteDatabase(str(tmp_path / "test.db"))
    create_tenants_table(database)
    repository = SQLiteTenantRepository(database)

    same_id = uuid4()
    tenant1 = Tenant(
        id=same_id,
        name="École A",
        slug="ecole-a",
        active=True,
    )
    repository.save(tenant1)

    tenant2 = Tenant(
        id=same_id,
        name="École B",
        slug="ecole-b",
        active=True,
    )
    with pytest.raises(sqlite3.IntegrityError):
        repository.save(tenant2)
