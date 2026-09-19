from uuid import uuid4

from src.domain.entities.academic_option import AcademicOption
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_academic_option_repository import (
    SQLiteAcademicOptionRepository,
)


def create_database():
    database = SQLiteDatabase(":memory:")
    database.initialize()
    return database


def seed_tenant(database, tenant_id):
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO tenants (
                id,
                name,
                slug,
                active
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                str(tenant_id),
                f"Tenant {tenant_id}",
                f"tenant-{tenant_id}",
                1,
            ),
        )


def test_save_and_find_academic_option_by_id():
    database = create_database()
    repository = SQLiteAcademicOptionRepository(database)

    tenant_id = uuid4()
    seed_tenant(database, tenant_id)

    academic_option = AcademicOption(
        id=uuid4(),
        tenant_id=tenant_id,
        name="Informatique",
        code="INFO",
    )

    repository.save(academic_option)

    result = repository.find_by_id(
        academic_option.id,
        tenant_id,
    )

    assert result is not None
    assert result.id == academic_option.id
    assert result.tenant_id == tenant_id
    assert result.name == "Informatique"
    assert result.code == "INFO"
    assert result.active is True


def test_find_academic_option_from_another_tenant_returns_none():
    database = create_database()
    repository = SQLiteAcademicOptionRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    seed_tenant(database, tenant_a)
    seed_tenant(database, tenant_b)

    academic_option = AcademicOption(
        id=uuid4(),
        tenant_id=tenant_a,
        name="Informatique",
        code="INFO",
    )

    repository.save(academic_option)

    result = repository.find_by_id(
        academic_option.id,
        tenant_b,
    )

    assert result is None


def test_find_unknown_academic_option_returns_none():
    database = create_database()
    repository = SQLiteAcademicOptionRepository(database)

    tenant_id = uuid4()
    seed_tenant(database, tenant_id)

    assert repository.find_by_id(
        uuid4(),
        tenant_id,
    ) is None
