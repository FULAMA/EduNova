import sqlite3

import pytest

from src.infrastructure.persistence.migrations.runner import MigrationRunner
from src.infrastructure.persistence.migrations.versions import (
    migration_002_academic_classes_tenant,
)


def create_legacy_academic_classes_table(connection):
    connection.execute("""
        CREATE TABLE academic_classes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)


def test_migration_002_adds_tenant_id_to_academic_classes():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_academic_classes_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_002_academic_classes_tenant)

    runner.run()

    columns = connection.execute("""
        PRAGMA table_info(academic_classes)
    """).fetchall()

    column_names = [column["name"] for column in columns]

    assert "tenant_id" in column_names


def test_migration_002_is_recorded():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_academic_classes_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_002_academic_classes_tenant)

    runner.run()

    row = connection.execute("""
        SELECT version
        FROM schema_migrations
        WHERE version = '002'
    """).fetchone()

    assert row is not None


def test_migration_002_rejects_null_tenant_id():
    connection = sqlite3.connect(":memory:")

    create_legacy_academic_classes_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_002_academic_classes_tenant)

    runner.run()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO academic_classes (
                id,
                name,
                tenant_id
            )
            VALUES (?, ?, ?)
        """, (
            "class-1",
            "6e Scientifique",
            None,
        ))



def test_migration_002_refuses_legacy_rows_without_tenant():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_academic_classes_table(connection)

    connection.execute("""
        INSERT INTO academic_classes (
            id,
            name
        )
        VALUES (?, ?)
    """, (
        "class-1",
        "6e Scientifique",
    ))

    runner = MigrationRunner(connection)
    runner.register_module(migration_002_academic_classes_tenant)

    with pytest.raises(
        RuntimeError,
        match="n'ont pas de tenant_id",
    ):
        runner.run()

    row = connection.execute("""
        SELECT id, name
        FROM academic_classes
        WHERE id = ?
    """, ("class-1",)).fetchone()

    assert row is not None
    assert row["id"] == "class-1"
    assert row["name"] == "6e Scientifique"

def test_migration_002_refuses_legacy_rows_without_tenant():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_academic_classes_table(connection)

    connection.execute("""
        INSERT INTO academic_classes (
            id,
            name
        )
        VALUES (?, ?)
    """, (
        "class-1",
        "6e Scientifique",
    ))

    runner = MigrationRunner(connection)
    runner.register_module(migration_002_academic_classes_tenant)

    with pytest.raises(
        RuntimeError,
        match="n'ont pas de tenant_id",
    ):
        runner.run()

    row = connection.execute("""
        SELECT id, name
        FROM academic_classes
        WHERE id = ?
    """, ("class-1",)).fetchone()

    assert row is not None
    assert row["id"] == "class-1"
    assert row["name"] == "6e Scientifique"
