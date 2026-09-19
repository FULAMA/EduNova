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
)


def create_legacy_schema(connection: sqlite3.Connection) -> None:
    connection.execute("""
        CREATE TABLE academic_classes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE subjects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            coefficient REAL NOT NULL,
            active INTEGER NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE academic_options (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            active INTEGER NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE class_options (
            id TEXT PRIMARY KEY,
            academic_class_id TEXT NOT NULL,
            academic_option_id TEXT NOT NULL,
            active INTEGER NOT NULL,
            UNIQUE (
                academic_class_id,
                academic_option_id
            )
        )
    """)

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
        CREATE TABLE students (
            id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            active INTEGER NOT NULL
        )
    """)

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


def run_all_migrations(connection: sqlite3.Connection) -> None:
    runner = MigrationRunner(connection)

    runner.register_module(migration_001_baseline)
    runner.register_module(migration_002_academic_classes_tenant)
    runner.register_module(migration_003_subjects_tenant)
    runner.register_module(migration_004_academic_options_tenant)
    runner.register_module(migration_005_class_options_tenant)
    runner.register_module(migration_006_class_subjects_tenant)
    runner.register_module(migration_007_tenant_scoped_uniqueness)
    runner.register_module(migration_008_cross_tenant_integrity)
    runner.register_module(migration_009_students_tenant)
    runner.register_module(migration_010_student_academic_records_tenant)

    runner.run()


def get_index_columns(
    connection: sqlite3.Connection,
    table_name: str,
) -> list[list[str]]:
    indexes = connection.execute(
        f'PRAGMA index_list("{table_name}")'
    ).fetchall()

    result = []

    for index in indexes:
        index_name = index[1]

        columns = connection.execute(
            f'PRAGMA index_info("{index_name}")'
        ).fetchall()

        result.append([column[2] for column in columns])

    return result


def test_all_migrations_run_in_order():
    connection = sqlite3.connect(":memory:")

    create_legacy_schema(connection)

    run_all_migrations(connection)

    migrations = connection.execute("""
        SELECT version
        FROM schema_migrations
        ORDER BY version
    """).fetchall()

    assert [row[0] for row in migrations] == [
        "001",
        "002",
        "003",
        "004",
        "005",
        "006",
        "007",
        "008",
        "009",
        "010",
    ]


def test_parent_tables_have_composite_unique_keys_for_tenant_integrity():
    connection = sqlite3.connect(":memory:")

    create_legacy_schema(connection)
    run_all_migrations(connection)

    assert ["tenant_id", "id"] in get_index_columns(
        connection,
        "academic_classes",
    )

    assert ["tenant_id", "id"] in get_index_columns(
        connection,
        "subjects",
    )

    assert ["tenant_id", "id"] in get_index_columns(
        connection,
        "academic_options",
    )


def test_all_academic_tables_contain_tenant_id():
    connection = sqlite3.connect(":memory:")

    create_legacy_schema(connection)
    run_all_migrations(connection)

    expected_tables = [
        "academic_classes",
        "subjects",
        "academic_options",
        "class_options",
        "class_subjects",
        "students",
        "student_academic_records",
    ]

    for table_name in expected_tables:
        columns = connection.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()

        column_names = [column[1] for column in columns]

        assert "tenant_id" in column_names, table_name

def test_cross_tenant_academic_relationship_is_rejected():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    create_legacy_schema(connection)
    run_all_migrations(connection)

    tenant_a = "tenant-a"
    tenant_b = "tenant-b"

    class_a = "class-a"
    class_b = "class-b"

    subject_a = "subject-a"
    subject_b = "subject-b"

    option_a = "option-a"
    option_b = "option-b"

    # Classes
    connection.execute(
        """
        INSERT INTO academic_classes (id, tenant_id, name)
        VALUES (?, ?, ?)
        """,
        (class_a, tenant_a, "Classe A"),
    )

    connection.execute(
        """
        INSERT INTO academic_classes (id, tenant_id, name)
        VALUES (?, ?, ?)
        """,
        (class_b, tenant_b, "Classe B"),
    )

    # Matières
    connection.execute(
        """
        INSERT INTO subjects (
            id, tenant_id, name, code, coefficient, active
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (subject_a, tenant_a, "Mathematiques A", "MATH", 2.0, 1),
    )

    connection.execute(
        """
        INSERT INTO subjects (
            id, tenant_id, name, code, coefficient, active
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (subject_b, tenant_b, "Mathematiques B", "MATH", 2.0, 1),
    )

    # Options
    connection.execute(
        """
        INSERT INTO academic_options (
            id, tenant_id, name, code, active
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (option_a, tenant_a, "Option A", "OPT", 1),
    )

    connection.execute(
        """
        INSERT INTO academic_options (
            id, tenant_id, name, code, active
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (option_b, tenant_b, "Option B", "OPT", 1),
    )

    connection.commit()

    # Même tenant ? autorisé
    connection.execute(
        """
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
        """,
        (
            "cs-a",
            tenant_a,
            class_a,
            subject_a,
            2.0,
            option_a,
            1,
        ),
    )

    # Tenant A + matière Tenant B ? interdit
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
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
            """,
            (
                "cs-cross-tenant",
                tenant_a,
                class_a,
                subject_b,
                2.0,
                option_a,
                1,
            ),
        )

    # Tenant B + classe Tenant A ? interdit
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
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
            """,
            (
                "cs-cross-tenant-2",
                tenant_b,
                class_a,
                subject_b,
                2.0,
                option_b,
                1,
            ),
        )

    connection.rollback()


