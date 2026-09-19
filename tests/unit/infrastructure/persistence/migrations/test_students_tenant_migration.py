import sqlite3

import pytest

from src.infrastructure.persistence.migrations.runner import MigrationRunner
from src.infrastructure.persistence.migrations.versions import (
    migration_009_students_tenant,
)


def create_legacy_students_table(connection):
    connection.execute("""
        CREATE TABLE students (
            id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            active INTEGER NOT NULL
        )
    """)


def run_migration(connection):
    runner = MigrationRunner(connection)
    runner.register_module(migration_009_students_tenant)
    runner.run()


def test_migration_009_adds_tenant_id_to_students():
    connection = sqlite3.connect(":memory:")

    create_legacy_students_table(connection)
    run_migration(connection)

    columns = connection.execute("""
        PRAGMA table_info(students)
    """).fetchall()

    column_names = [column[1] for column in columns]

    assert "tenant_id" in column_names


def test_migration_009_rejects_null_tenant_id():
    connection = sqlite3.connect(":memory:")

    create_legacy_students_table(connection)
    run_migration(connection)

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO students (
                id,
                tenant_id,
                first_name,
                last_name,
                email,
                phone,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "student-1",
            None,
            "Isaac",
            "Fulama",
            "isaac@example.com",
            None,
            1,
        ))


def test_migration_009_refuses_legacy_students_without_tenant():
    connection = sqlite3.connect(":memory:")

    create_legacy_students_table(connection)

    connection.execute("""
        INSERT INTO students (
            id,
            first_name,
            last_name,
            email,
            phone,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "student-1",
        "Isaac",
        "Fulama",
        "isaac@example.com",
        None,
        1,
    ))

    runner = MigrationRunner(connection)
    runner.register_module(migration_009_students_tenant)

    with pytest.raises(
        RuntimeError,
        match="n'ont pas de tenant_id",
    ):
        runner.run()

    row = connection.execute("""
        SELECT
            id,
            first_name,
            last_name
        FROM students
        WHERE id = ?
    """, ("student-1",)).fetchone()

    assert row is not None
    assert row[0] == "student-1"
    assert row[1] == "Isaac"
    assert row[2] == "Fulama"


def test_migration_009_preserves_student_data():
    connection = sqlite3.connect(":memory:")

    create_legacy_students_table(connection)

    connection.execute("""
        INSERT INTO students (
            id,
            first_name,
            last_name,
            email,
            phone,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "student-1",
        "Isaac",
        "Fulama",
        "isaac@example.com",
        "+243000000000",
        1,
    ))

    # Une table legacy contenant des données ne peut pas être
    # migrée automatiquement sans attribution explicite d'un tenant.
    runner = MigrationRunner(connection)
    runner.register_module(migration_009_students_tenant)

    with pytest.raises(RuntimeError):
        runner.run()

    row = connection.execute("""
        SELECT
            first_name,
            last_name,
            email,
            phone,
            active
        FROM students
        WHERE id = ?
    """, ("student-1",)).fetchone()

    assert tuple(row) == (
        "Isaac",
        "Fulama",
        "isaac@example.com",
        "+243000000000",
        1,
    )
