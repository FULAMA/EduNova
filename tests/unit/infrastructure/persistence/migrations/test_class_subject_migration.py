import sqlite3

import pytest

from src.infrastructure.persistence.migrations.runner import MigrationRunner
from src.infrastructure.persistence.migrations.versions import (
    migration_006_class_subjects_tenant,
)


def create_legacy_class_subjects_table(connection):
    connection.execute("""
        CREATE TABLE class_subjects (
            id TEXT PRIMARY KEY,
            academic_class_id TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            coefficient REAL NOT NULL,
            academic_option_id TEXT,
            active INTEGER NOT NULL,
            UNIQUE (
                academic_class_id,
                subject_id,
                academic_option_id
            )
        )
    """)

    connection.execute("""
        CREATE UNIQUE INDEX uq_class_subject_common
        ON class_subjects (
            academic_class_id,
            subject_id
        )
        WHERE academic_option_id IS NULL
    """)


def test_migration_006_adds_tenant_id_to_class_subjects():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_class_subjects_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_006_class_subjects_tenant)

    runner.run()

    columns = connection.execute("""
        PRAGMA table_info(class_subjects)
    """).fetchall()

    column_names = [column["name"] for column in columns]

    assert "tenant_id" in column_names


def test_migration_006_rejects_null_tenant_id():
    connection = sqlite3.connect(":memory:")

    create_legacy_class_subjects_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_006_class_subjects_tenant)

    runner.run()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO class_subjects (
                id,
                tenant_id,
                academic_class_id,
                subject_id,
                coefficient,
                academic_option_id,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "class-subject-1",
            None,
            "class-1",
            "subject-1",
            2.0,
            None,
            1,
        ))


def test_migration_006_refuses_legacy_rows_without_tenant():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_legacy_class_subjects_table(connection)

    connection.execute("""
        INSERT INTO class_subjects (
            id,
            academic_class_id,
            subject_id,
            coefficient,
            academic_option_id,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "class-subject-1",
        "class-1",
        "subject-1",
        2.0,
        None,
        1,
    ))

    runner = MigrationRunner(connection)
    runner.register_module(migration_006_class_subjects_tenant)

    with pytest.raises(
        RuntimeError,
        match="n'ont pas de tenant_id",
    ):
        runner.run()

    row = connection.execute("""
        SELECT
            id,
            academic_class_id,
            subject_id
        FROM class_subjects
        WHERE id = ?
    """, ("class-subject-1",)).fetchone()

    assert row is not None
    assert row["id"] == "class-subject-1"
    assert row["academic_class_id"] == "class-1"
    assert row["subject_id"] == "subject-1"


def test_migration_006_preserves_common_subject_unique_index():
    connection = sqlite3.connect(":memory:")

    create_legacy_class_subjects_table(connection)

    runner = MigrationRunner(connection)
    runner.register_module(migration_006_class_subjects_tenant)

    runner.run()

    connection.execute("""
        INSERT INTO class_subjects (
            id,
            tenant_id,
            academic_class_id,
            subject_id,
            coefficient,
            academic_option_id,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "class-subject-1",
        "tenant-1",
        "class-1",
        "subject-1",
        2.0,
        None,
        1,
    ))

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO class_subjects (
                id,
                tenant_id,
                academic_class_id,
                subject_id,
                coefficient,
                academic_option_id,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "class-subject-2",
            "tenant-1",
            "class-1",
            "subject-1",
            3.0,
            None,
            1,
        ))
