import sqlite3

import pytest

from src.infrastructure.persistence.migrations.runner import MigrationRunner
from src.infrastructure.persistence.migrations.versions import (
    migration_001_baseline,
    migration_002_academic_classes_tenant,
    migration_003_subjects_tenant,
    migration_004_academic_options_tenant,
    migration_005_class_options_tenant,
    migration_006_class_subjects_tenant,
    migration_007_tenant_scoped_uniqueness,
    migration_008_cross_tenant_integrity,
    migration_009_students_tenant,
    migration_010_student_academic_records_tenant,
    migration_011_student_record_integrity,
)


def create_legacy_schema(connection: sqlite3.Connection) -> None:
    connection.executescript("""
        CREATE TABLE academic_classes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE subjects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            coefficient REAL NOT NULL,
            active INTEGER NOT NULL
        );

        CREATE TABLE academic_options (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            active INTEGER NOT NULL
        );

        CREATE TABLE class_options (
            id TEXT PRIMARY KEY,
            academic_class_id TEXT NOT NULL,
            academic_option_id TEXT NOT NULL,
            active INTEGER NOT NULL
        );

        CREATE TABLE class_subjects (
            id TEXT PRIMARY KEY,
            academic_class_id TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            coefficient REAL NOT NULL,
            academic_option_id TEXT,
            active INTEGER NOT NULL
        );

        CREATE TABLE students (
            id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            active INTEGER NOT NULL
        );

        CREATE TABLE student_academic_records (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            general_average REAL NOT NULL,
            failed_subjects INTEGER NOT NULL,
            credits_obtained REAL NOT NULL,
            total_credits REAL NOT NULL,
            PRIMARY KEY (student_id, academic_period_id)
        );
    """)


def run_all_migrations(connection: sqlite3.Connection) -> None:
    runner = MigrationRunner(connection)

    migrations = [
        migration_001_baseline,
        migration_002_academic_classes_tenant,
        migration_003_subjects_tenant,
        migration_004_academic_options_tenant,
        migration_005_class_options_tenant,
        migration_006_class_subjects_tenant,
        migration_007_tenant_scoped_uniqueness,
        migration_008_cross_tenant_integrity,
        migration_009_students_tenant,
        migration_010_student_academic_records_tenant,
        migration_011_student_record_integrity,
    ]

    for migration in migrations:
        runner.register_module(migration)

    runner.run()


def test_student_record_must_belong_to_same_tenant():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    create_legacy_schema(connection)
    run_all_migrations(connection)

    tenant_a = "tenant-a"
    tenant_b = "tenant-b"

    student_a = "student-a"
    student_b = "student-b"

    connection.execute(
        """
        INSERT INTO students (
            id, tenant_id, first_name, last_name, email, phone, active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student_a,
            tenant_a,
            "Jean",
            "A",
            None,
            None,
            1,
        ),
    )

    connection.execute(
        """
        INSERT INTO students (
            id, tenant_id, first_name, last_name, email, phone, active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student_b,
            tenant_b,
            "Paul",
            "B",
            None,
            None,
            1,
        ),
    )

    # Même tenant : autorisé.
    connection.execute(
        """
        INSERT INTO student_academic_records (
            student_id,
            academic_period_id,
            tenant_id,
            general_average,
            failed_subjects,
            credits_obtained,
            total_credits
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student_a,
            "period-a",
            tenant_a,
            15.0,
            0,
            30.0,
            30.0,
        ),
    )

    # Tenant A + étudiant du Tenant B : interdit.
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO student_academic_records (
                student_id,
                academic_period_id,
                tenant_id,
                general_average,
                failed_subjects,
                credits_obtained,
                total_credits
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_b,
                "period-b",
                tenant_a,
                14.0,
                1,
                28.0,
                30.0,
            ),
        )


def test_students_have_composite_tenant_key():
    connection = sqlite3.connect(":memory:")

    create_legacy_schema(connection)
    run_all_migrations(connection)

    indexes = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'index'
        AND tbl_name = 'students'
        """
    ).fetchall()

    index_names = {row[0] for row in indexes}

    assert "uq_students_tenant_id" in index_names
