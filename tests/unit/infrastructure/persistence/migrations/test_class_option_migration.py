import sqlite3

import pytest

from src.infrastructure.persistence.migrations.runner import MigrationRunner
from src.infrastructure.persistence.migrations.versions import (
    migration_005_class_options_tenant,
)


def create_legacy_class_options_table(connection):
    connection.execute("""
        CREATE TABLE class_options (
            id TEXT PRIMARY KEY,
            academic_class_id TEXT NOT NULL,
            academic_option_id TEXT NOT NULL,
            active INTEGER NOT NULL,
            UNIQUE (academic_class_id, academic_option_id)
        )
    """)


def test_migration_005_adds_tenant_id_to_class_options():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_class_options_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_005_class_options_tenant)

    runner.run()

    columns = connection.execute("""
        PRAGMA table_info(class_options)
    """).fetchall()

    column_names = [column["name"] for column in columns]

    assert "tenant_id" in column_names


def test_migration_005_rejects_null_tenant_id():
    connection = sqlite3.connect(":memory:")

    create_legacy_class_options_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_005_class_options_tenant)

    runner.run()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO class_options (
                id,
                tenant_id,
                academic_class_id,
                academic_option_id,
                active
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            "class-option-1",
            None,
            "class-1",
            "option-1",
            1,
        ))


def test_migration_005_refuses_legacy_rows_without_tenant():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_class_options_table(connection)

    connection.execute("""
        INSERT INTO class_options (
            id,
            academic_class_id,
            academic_option_id,
            active
        )
        VALUES (?, ?, ?, ?)
    """, (
        "class-option-1",
        "class-1",
        "option-1",
        1,
    ))

    runner = MigrationRunner(connection)
    runner.register_module(migration_005_class_options_tenant)

    with pytest.raises(
        RuntimeError,
        match="n'ont pas de tenant_id",
    ):
        runner.run()

    row = connection.execute("""
        SELECT id, academic_class_id, academic_option_id
        FROM class_options
        WHERE id = ?
    """, ("class-option-1",)).fetchone()

    assert row is not None
    assert row["id"] == "class-option-1"
    assert row["academic_class_id"] == "class-1"
    assert row["academic_option_id"] == "option-1"
