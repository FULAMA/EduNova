import sqlite3

import pytest

from src.infrastructure.persistence.migrations.runner import MigrationRunner
from src.infrastructure.persistence.migrations.versions import (
    migration_007_tenant_scoped_uniqueness,
)


def create_migrated_tables(connection):
    connection.execute("""
        CREATE TABLE subjects (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            coefficient REAL NOT NULL,
            active INTEGER NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE academic_options (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            active INTEGER NOT NULL
        )
    """)


def run_migration(connection):
    runner = MigrationRunner(connection)
    runner.register_module(migration_007_tenant_scoped_uniqueness)
    runner.run()


def test_migration_007_allows_same_subject_code_in_different_tenants():
    connection = sqlite3.connect(":memory:")

    create_migrated_tables(connection)
    run_migration(connection)

    connection.execute("""
        INSERT INTO subjects (
            id, tenant_id, name, code, coefficient, active
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "subject-1",
        "tenant-1",
        "Mathématiques",
        "MATH",
        2.0,
        1,
    ))

    connection.execute("""
        INSERT INTO subjects (
            id, tenant_id, name, code, coefficient, active
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "subject-2",
        "tenant-2",
        "Mathématiques",
        "MATH",
        2.0,
        1,
    ))


def test_migration_007_rejects_duplicate_subject_code_in_same_tenant():
    connection = sqlite3.connect(":memory:")

    create_migrated_tables(connection)
    run_migration(connection)

    connection.execute("""
        INSERT INTO subjects (
            id, tenant_id, name, code, coefficient, active
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "subject-1",
        "tenant-1",
        "Mathématiques",
        "MATH",
        2.0,
        1,
    ))

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO subjects (
                id, tenant_id, name, code, coefficient, active
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "subject-2",
            "tenant-1",
            "Algèbre",
            "MATH",
            3.0,
            1,
        ))


def test_migration_007_allows_same_option_code_in_different_tenants():
    connection = sqlite3.connect(":memory:")

    create_migrated_tables(connection)
    run_migration(connection)

    connection.execute("""
        INSERT INTO academic_options (
            id, tenant_id, name, code, active
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        "option-1",
        "tenant-1",
        "Scientifique",
        "SCI",
        1,
    ))

    connection.execute("""
        INSERT INTO academic_options (
            id, tenant_id, name, code, active
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        "option-2",
        "tenant-2",
        "Scientifique",
        "SCI",
        1,
    ))


def test_migration_007_rejects_duplicate_option_code_in_same_tenant():
    connection = sqlite3.connect(":memory:")

    create_migrated_tables(connection)
    run_migration(connection)

    connection.execute("""
        INSERT INTO academic_options (
            id, tenant_id, name, code, active
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        "option-1",
        "tenant-1",
        "Scientifique",
        "SCI",
        1,
    ))

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO academic_options (
                id, tenant_id, name, code, active
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            "option-2",
            "tenant-1",
            "Littéraire",
            "SCI",
            1,
        ))
