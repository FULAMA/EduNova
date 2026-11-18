import sqlite3
from uuid import uuid4

import pytest

from src.identity.domain.entities.user import User
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository
from src.tenancy.application.interfaces.establishment_provisioning_unit_of_work import (
    EstablishmentProvisioningConflict,
)
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant
from src.tenancy.infrastructure.persistence.sqlite_establishment_provisioning_uow import (
    SQLiteEstablishmentProvisioningUnitOfWork,
)
from src.tenancy.infrastructure.repositories.sqlite_membership_repository import (
    SQLiteMembershipRepository,
)
from src.tenancy.infrastructure.repositories.sqlite_tenant_repository import (
    SQLiteTenantRepository,
)


def create_test_db(db_path: str) -> SQLiteDatabase:
    database = SQLiteDatabase(db_path)
    with database.connect() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                active INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                two_factor_enabled INTEGER NOT NULL,
                two_factor_secret TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memberships (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                role TEXT NOT NULL,
                active INTEGER NOT NULL,
                UNIQUE (user_id, tenant_id),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
            )
            """
        )
    return database


def test_provision_establishment_atomic_success(tmp_path):
    db_path = str(tmp_path / "test_success.db")
    db = create_test_db(db_path)

    tenant_repo = SQLiteTenantRepository(db)
    user_repo = SQLiteUserRepository(db)
    membership_repo = SQLiteMembershipRepository(db)
    uow = SQLiteEstablishmentProvisioningUnitOfWork(
        database=db,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        membership_repository=membership_repo,
    )

    tenant = Tenant(
        id=uuid4(),
        name="Lycée Prince de Liège",
        slug="lycee-prince-de-liege",
        active=True,
    )
    user = User(
        id=uuid4(),
        email="direction@prince-liege.cd",
        password_hash="argon2id$mocked$hash",
        role="ADMIN",
        is_active=True,
    )
    membership = Membership(
        id=uuid4(),
        user_id=user.id,
        tenant_id=tenant.id,
        role="ADMIN",
        active=True,
    )

    uow.provision_establishment_atomic(tenant, user, membership)

    # Verify all three entities exist in DB
    saved_tenant = tenant_repo.find_by_id(tenant.id)
    assert saved_tenant is not None
    assert saved_tenant.slug == "lycee-prince-de-liege"

    saved_user = user_repo.find_by_email("direction@prince-liege.cd")
    assert saved_user is not None
    assert saved_user.id == user.id

    saved_membership = membership_repo.find_by_user_and_tenant(user.id, tenant.id)
    assert saved_membership is not None
    assert saved_membership.role == "ADMIN"
    assert saved_membership.active is True


def test_provision_establishment_rollback_on_user_duplicate_email(tmp_path):
    db_path = str(tmp_path / "test_rollback_user.db")
    db = create_test_db(db_path)

    tenant_repo = SQLiteTenantRepository(db)
    user_repo = SQLiteUserRepository(db)
    membership_repo = SQLiteMembershipRepository(db)
    uow = SQLiteEstablishmentProvisioningUnitOfWork(
        database=db,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        membership_repository=membership_repo,
    )

    # Pre-seed an existing user with this email
    existing_user = User(
        id=uuid4(),
        email="existing@edunova.cd",
        password_hash="hash1",
        role="USER",
        is_active=True,
    )
    user_repo.save(existing_user)

    # Attempt to provision with the same email
    tenant = Tenant(
        id=uuid4(),
        name="École Nouvelle",
        slug="ecole-nouvelle",
        active=True,
    )
    conflicting_user = User(
        id=uuid4(),  # Different ID, same email
        email="existing@edunova.cd",
        password_hash="hash2",
        role="ADMIN",
        is_active=True,
    )
    membership = Membership(
        id=uuid4(),
        user_id=conflicting_user.id,
        tenant_id=tenant.id,
        role="ADMIN",
        active=True,
    )

    with pytest.raises((sqlite3.IntegrityError, EstablishmentProvisioningConflict)):
        uow.provision_establishment_atomic(tenant, conflicting_user, membership)

    # Verify atomic rollback: the Tenant was NOT committed!
    assert tenant_repo.find_by_id(tenant.id) is None
    assert tenant_repo.find_by_slug("ecole-nouvelle") is None
    # Membership was NOT committed
    assert membership_repo.find_by_id(membership.id) is None


def test_provision_establishment_rollback_on_membership_failure(tmp_path):
    db_path = str(tmp_path / "test_rollback_membership.db")
    db = create_test_db(db_path)

    tenant_repo = SQLiteTenantRepository(db)
    user_repo = SQLiteUserRepository(db)
    membership_repo = SQLiteMembershipRepository(db)
    uow = SQLiteEstablishmentProvisioningUnitOfWork(
        database=db,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        membership_repository=membership_repo,
    )

    tenant = Tenant(
        id=uuid4(),
        name="Institut Saint Joseph",
        slug="saint-joseph",
        active=True,
    )
    user = User(
        id=uuid4(),
        email="admin@saint-joseph.cd",
        password_hash="hash_sj",
        role="ADMIN",
        is_active=True,
    )
    # Pre-seed a membership with the exact same ID to force unique constraint violation on memberships table
    collision_id = uuid4()
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO tenants (id, name, slug, active) VALUES (?, ?, ?, ?)",
            (str(uuid4()), "Seed", "seed-slug", 1),
        )
        # Using a dummy user and tenant
        conn.execute(
            "INSERT INTO users (id, email, password_hash, role, is_active, two_factor_enabled) VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid4()), "dummy@seed.cd", "h", "A", 1, 0),
        )
        conn.execute(
            "INSERT INTO memberships (id, user_id, tenant_id, role, active) VALUES (?, (SELECT id FROM users LIMIT 1), (SELECT id FROM tenants LIMIT 1), 'ADMIN', 1)",
            (str(collision_id),),
        )

    # Conflicting membership ID
    membership = Membership(
        id=collision_id,
        user_id=user.id,
        tenant_id=tenant.id,
        role="ADMIN",
        active=True,
    )

    with pytest.raises((sqlite3.IntegrityError, EstablishmentProvisioningConflict)):
        uow.provision_establishment_atomic(tenant, user, membership)

    # Verify atomic rollback: neither Tenant nor User were persisted!
    assert tenant_repo.find_by_id(tenant.id) is None
    assert user_repo.find_by_id(user.id) is None
    assert user_repo.find_by_email("admin@saint-joseph.cd") is None


def test_relational_cascade_on_tenant_deletion(tmp_path):
    db_path = str(tmp_path / "test_cascade.db")
    db = create_test_db(db_path)

    tenant_repo = SQLiteTenantRepository(db)
    user_repo = SQLiteUserRepository(db)
    membership_repo = SQLiteMembershipRepository(db)
    uow = SQLiteEstablishmentProvisioningUnitOfWork(
        database=db,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        membership_repository=membership_repo,
    )

    tenant = Tenant(id=uuid4(), name="École Test", slug="ecole-test", active=True)
    user = User(id=uuid4(), email="u@test.cd", password_hash="h", role="ADMIN", is_active=True)
    membership = Membership(id=uuid4(), user_id=user.id, tenant_id=tenant.id, role="ADMIN", active=True)

    uow.provision_establishment_atomic(tenant, user, membership)
    assert membership_repo.find_by_id(membership.id) is not None

    # Delete tenant: cascade should remove membership
    with db.connect() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM tenants WHERE id = ?", (str(tenant.id),))

    assert membership_repo.find_by_id(membership.id) is None
    # User remains intact (not deleted by tenant deletion)
    assert user_repo.find_by_id(user.id) is not None
