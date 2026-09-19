import sqlite3

import pytest

from src.infrastructure.persistence.migrations.runner import MigrationRunner
from src.infrastructure.persistence.migrations.versions import (
    migration_003_subjects_tenant,
)


def create_legacy_subjects_table(connection):
    connection.execute("""
        CREATE TABLE subjects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            coefficient REAL NOT NULL,
            active INTEGER NOT NULL
        )
    """)


def test_migration_003_adds_tenant_id_to_subjects():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_subjects_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_003_subjects_tenant)

    runner.run()

    columns = connection.execute("""
        PRAGMA table_info(subjects)
    """).fetchall()

    column_names = [column["name"] for column in columns]

    assert "tenant_id" in column_names


def test_migration_003_rejects_null_tenant_id():
    connection = sqlite3.connect(":memory:")

    create_legacy_subjects_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_003_subjects_tenant)

    runner.run()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO subjects (
                id,
                tenant_id,
                name,
                code,
                coefficient,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "subject-1",
            None,
            "Mathématiques",
            "MATH",
            2.0,
            1,
        ))


def test_migration_003_refuses_legacy_rows_without_tenant():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_subjects_table(connection)

    connection.execute("""
        INSERT INTO subjects (
            id,
            name,
            code,
            coefficient,
            active
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        "subject-1",
        "Mathématiques",
        "MATH",
        2.0,
        1,
    ))

    runner = MigrationRunner(connection)
    runner.register_module(migration_003_subjects_tenant)

    with pytest.raises(
        RuntimeError,
        match="n'ont pas de tenant_id",
    ):
        runner.run()

    row = connection.execute("""
        SELECT id, name, code
        FROM subjects
        WHERE id = ?
    """, ("subject-1",)).fetchone()

    assert row is not None
    assert row["id"] == "subject-1"
    assert row["name"] == "Mathématiques"
    assert row["code"] == "MATH"
