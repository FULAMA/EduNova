import sqlite3

import pytest

from src.infrastructure.persistence.migrations.runner import MigrationRunner
from src.infrastructure.persistence.migrations.versions import (
    migration_008_cross_tenant_integrity,
)


def create_parent_tables(connection):
    connection.execute("""
        CREATE TABLE academic_classes (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE UNIQUE INDEX uq_academic_classes_tenant_id
        ON academic_classes (
            tenant_id,
            id
        )
    """)

    connection.execute("""
        CREATE TABLE subjects (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE UNIQUE INDEX uq_subjects_tenant_id
        ON subjects (
            tenant_id,
            id
        )
    """)

    connection.execute("""
        CREATE TABLE academic_options (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE UNIQUE INDEX uq_academic_options_tenant_id
        ON academic_options (
            tenant_id,
            id
        )
    """)


def create_class_subjects_table(connection):
    connection.execute("""
        CREATE TABLE class_subjects (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
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


def create_class_options_table(connection):
    connection.execute("""
        CREATE TABLE class_options (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            academic_class_id TEXT NOT NULL,
            academic_option_id TEXT NOT NULL,
            active INTEGER NOT NULL,
            UNIQUE (
                academic_class_id,
                academic_option_id
            )
        )
    """)


def run_migration(connection):
    runner = MigrationRunner(connection)
    runner.register_module(migration_008_cross_tenant_integrity)
    runner.run()


def insert_parent_data(connection):
    connection.execute("""
        INSERT INTO academic_classes (
            id,
            tenant_id,
            name
        )
        VALUES (?, ?, ?)
    """, (
        "class-a",
        "tenant-a",
        "6e Scientifique",
    ))

    connection.execute("""
        INSERT INTO academic_classes (
            id,
            tenant_id,
            name
        )
        VALUES (?, ?, ?)
    """, (
        "class-b",
        "tenant-b",
        "6e Scientifique",
    ))

    connection.execute("""
        INSERT INTO subjects (
            id,
            tenant_id,
            name,
            code
        )
        VALUES (?, ?, ?, ?)
    """, (
        "subject-a",
        "tenant-a",
        "Mathématiques",
        "MATH",
    ))

    connection.execute("""
        INSERT INTO subjects (
            id,
            tenant_id,
            name,
            code
        )
        VALUES (?, ?, ?, ?)
    """, (
        "subject-b",
        "tenant-b",
        "Mathématiques",
        "MATH",
    ))

    connection.execute("""
        INSERT INTO academic_options (
            id,
            tenant_id,
            name,
            code
        )
        VALUES (?, ?, ?, ?)
    """, (
        "option-a",
        "tenant-a",
        "Scientifique",
        "SCI",
    ))

    connection.execute("""
        INSERT INTO academic_options (
            id,
            tenant_id,
            name,
            code
        )
        VALUES (?, ?, ?, ?)
    """, (
        "option-b",
        "tenant-b",
        "Scientifique",
        "SCI",
    ))


def test_migration_008_allows_same_tenant_class_subject():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    create_parent_tables(connection)
    create_class_subjects_table(connection)
    create_class_options_table(connection)
    insert_parent_data(connection)

    run_migration(connection)

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
        "class-subject-a",
        "tenant-a",
        "class-a",
        "subject-a",
        2.0,
        None,
        1,
    ))


def test_migration_008_rejects_cross_tenant_class_subject():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    create_parent_tables(connection)
    create_class_subjects_table(connection)
    create_class_options_table(connection)
    insert_parent_data(connection)

    run_migration(connection)

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
            "invalid-relation",
            "tenant-a",
            "class-a",
            "subject-b",
            2.0,
            None,
            1,
        ))


def test_migration_008_rejects_cross_tenant_class_option():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    create_parent_tables(connection)
    create_class_subjects_table(connection)
    create_class_options_table(connection)
    insert_parent_data(connection)

    run_migration(connection)

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
            "invalid-relation",
            "tenant-a",
            "class-a",
            "option-b",
            1,
        ))
