import sqlite3

import pytest

from src.infrastructure.persistence.migrations.runner import MigrationRunner
from src.infrastructure.persistence.migrations.versions import (
    migration_004_academic_options_tenant,
)


def create_legacy_academic_options_table(connection):
    connection.execute("""
        CREATE TABLE academic_options (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            active INTEGER NOT NULL
        )
    """)


def test_migration_004_adds_tenant_id_to_academic_options():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_academic_options_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_004_academic_options_tenant)

    runner.run()

    columns = connection.execute("""
        PRAGMA table_info(academic_options)
    """).fetchall()

    column_names = [column["name"] for column in columns]

    assert "tenant_id" in column_names


def test_migration_004_rejects_null_tenant_id():
    connection = sqlite3.connect(":memory:")

    create_legacy_academic_options_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_004_academic_options_tenant)

    runner.run()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO academic_options (
                id,
                tenant_id,
                name,
                code,
                active
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            "option-1",
            None,
            "Scientifique",
            "SC",
            1,
        ))


def test_migration_004_refuses_legacy_rows_without_tenant():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_academic_options_table(connection)

    connection.execute("""
        INSERT INTO academic_options (
            id,
            name,
            code,
            active
        )
        VALUES (?, ?, ?, ?)
    """, (
        "option-1",
        "Scientifique",
        "SC",
        1,
    ))

    runner = MigrationRunner(connection)
    runner.register_module(migration_004_academic_options_tenant)

    with pytest.raises(
        RuntimeError,
        match="n'ont pas de tenant_id",
    ):
        runner.run()

    row = connection.execute("""
        SELECT id, name, code
        FROM academic_options
        WHERE id = ?
    """, ("option-1",)).fetchone()

    assert row is not None
    assert row["id"] == "option-1"
    assert row["name"] == "Scientifique"
    assert row["code"] == "SC"
