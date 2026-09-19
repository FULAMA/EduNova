import sqlite3

import pytest

from src.infrastructure.persistence.migrations.runner import MigrationRunner
from src.infrastructure.persistence.migrations.versions import (
    migration_010_student_academic_records_tenant,
)


def create_legacy_table(connection):
    connection.execute("""
        CREATE TABLE student_academic_records (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            general_average REAL NOT NULL,
            failed_subjects INTEGER NOT NULL,
            credits_obtained REAL NOT NULL,
            total_credits REAL NOT NULL,
            PRIMARY KEY (
                student_id,
                academic_period_id
            )
        )
    """)


def run_migration(connection):
    runner = MigrationRunner(connection)
    runner.register_module(
        migration_010_student_academic_records_tenant
    )
    runner.run()


def test_migration_010_adds_tenant_id():
    connection = sqlite3.connect(":memory:")

    create_legacy_table(connection)
    run_migration(connection)

    columns = connection.execute("""
        PRAGMA table_info(student_academic_records)
    """).fetchall()

    column_names = [column[1] for column in columns]

    assert "tenant_id" in column_names


def test_migration_010_rejects_null_tenant_id():
    connection = sqlite3.connect(":memory:")

    create_legacy_table(connection)
    run_migration(connection)

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
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
        """, (
            "student-1",
            "period-1",
            None,
            15.5,
            1,
            45,
            60,
        ))


def test_migration_010_refuses_legacy_records_without_tenant():
    connection = sqlite3.connect(":memory:")

    create_legacy_table(connection)

    connection.execute("""
        INSERT INTO student_academic_records (
            student_id,
            academic_period_id,
            general_average,
            failed_subjects,
            credits_obtained,
            total_credits
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "student-1",
        "period-1",
        15.5,
        1,
        45,
        60,
    ))

    runner = MigrationRunner(connection)
    runner.register_module(
        migration_010_student_academic_records_tenant
    )

    with pytest.raises(
        RuntimeError,
        match="n'ont pas de tenant_id",
    ):
        runner.run()

    row = connection.execute("""
        SELECT
            student_id,
            academic_period_id,
            general_average
        FROM student_academic_records
        WHERE student_id = ?
    """, ("student-1",)).fetchone()

    assert row is not None
    assert row[0] == "student-1"
    assert row[1] == "period-1"
    assert row[2] == 15.5


def test_migration_010_preserves_primary_key():
    connection = sqlite3.connect(":memory:")

    create_legacy_table(connection)
    run_migration(connection)

    connection.execute("""
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
    """, (
        "student-1",
        "period-1",
        "tenant-1",
        15.5,
        1,
        45,
        60,
    ))

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
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
        """, (
            "student-1",
            "period-1",
            "tenant-1",
            16.0,
            0,
            60,
            60,
        ))
