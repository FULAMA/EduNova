from uuid import uuid4

from src.domain.entities.membership import Membership
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_membership_repository import (
    SQLiteMembershipRepository,
)


def create_database():
    database = SQLiteDatabase(":memory:")
    database.initialize()
    return database


def create_membership(
    *,
    user_id=None,
    tenant_id=None,
    role="ADMIN",
    active=True,
):
    return Membership(
        id=uuid4(),
        user_id=user_id or uuid4(),
        tenant_id=tenant_id or uuid4(),
        role=role,
        active=active,
    )


def seed_user(database, user_id):
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO users (
                id,
                email,
                password_hash,
                role,
                is_active,
                two_factor_enabled,
                two_factor_secret
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(user_id),
                f"{user_id}@edunova.com",
                "hashed-password",
                "ADMIN",
                1,
                0,
                None,
            ),
        )


def seed_tenant(database, tenant_id):
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO tenants (id, name, slug, active)
            VALUES (?, ?, ?, ?)
            """,
            (
                str(tenant_id),
                f"Tenant {tenant_id}",
                f"tenant-{tenant_id}",
                1,
            ),
        )


def test_save_and_find_membership_by_id():
    database = create_database()
    repository = SQLiteMembershipRepository(database)

    user_id = uuid4()
    tenant_id = uuid4()

    seed_user(database, user_id)
    seed_tenant(database, tenant_id)

    membership = create_membership(
        user_id=user_id,
        tenant_id=tenant_id,
        role="ADMIN",
        active=True,
    )

    repository.save(membership)

    result = repository.find_by_id(membership.id)

    assert result is not None
    assert result.id == membership.id
    assert result.user_id == membership.user_id
    assert result.tenant_id == membership.tenant_id
    assert result.role == membership.role
    assert result.active is True


def test_find_unknown_membership_returns_none():
    database = create_database()
    repository = SQLiteMembershipRepository(database)

    assert repository.find_by_id(uuid4()) is None


def test_find_memberships_by_user():
    database = create_database()
    repository = SQLiteMembershipRepository(database)

    user_id = uuid4()
    tenant_id_1 = uuid4()
    tenant_id_2 = uuid4()

    seed_user(database, user_id)
    seed_tenant(database, tenant_id_1)
    seed_tenant(database, tenant_id_2)

    membership_1 = create_membership(
        user_id=user_id,
        tenant_id=tenant_id_1,
        role="ADMIN",
    )
    membership_2 = create_membership(
        user_id=user_id,
        tenant_id=tenant_id_2,
        role="TEACHER",
    )

    repository.save(membership_1)
    repository.save(membership_2)

    result = repository.find_by_user(user_id)

    assert len(result) == 2
    assert {membership.tenant_id for membership in result} == {
        tenant_id_1,
        tenant_id_2,
    }


def test_find_membership_by_user_and_tenant():
    database = create_database()
    repository = SQLiteMembershipRepository(database)

    user_id = uuid4()
    tenant_id = uuid4()

    seed_user(database, user_id)
    seed_tenant(database, tenant_id)

    membership = create_membership(
        user_id=user_id,
        tenant_id=tenant_id,
        role="TEACHER",
    )

    repository.save(membership)

    result = repository.find_by_user_and_tenant(
        user_id,
        tenant_id,
    )

    assert result is not None
    assert result.id == membership.id
    assert result.role == "TEACHER"


def test_find_membership_by_user_and_unknown_tenant_returns_none():
    database = create_database()
    repository = SQLiteMembershipRepository(database)

    user_id = uuid4()
    tenant_id = uuid4()

    seed_user(database, user_id)
    seed_tenant(database, tenant_id)

    membership = create_membership(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    repository.save(membership)

    assert repository.find_by_user_and_tenant(
        user_id,
        uuid4(),
    ) is None

