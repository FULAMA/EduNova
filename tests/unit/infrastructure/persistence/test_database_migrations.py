
import pytest

from src.infrastructure.persistence.database import SQLiteDatabase


def _create_ambiguous_legacy_database(database: SQLiteDatabase) -> None:
    connection = database.connect()
    connection.execute(
        """
        CREATE TABLE students (
            id TEXT PRIMARY KEY,
            student_number TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            active INTEGER NOT NULL,
            tenant_id TEXT
        )
        """
    )
    connection.execute(
        """
        INSERT INTO students (
            id,
            student_number,
            first_name,
            last_name,
            date_of_birth,
            active,
            tenant_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "student-1",
            "EDU-1",
            "Isaac",
            "Fulama",
            "2004-05-15",
            1,
            None,
        ),
    )
    connection.commit()


def test_initialize_applies_database_migrations():
    database = SQLiteDatabase(":memory:")

    database.initialize()

    connection = database.connect()

    migration = connection.execute("""
        SELECT version
        FROM schema_migrations
        WHERE version = '012'
    """).fetchone()

    assert migration is not None


def test_initialize_creates_tenant_scoped_academic_classes():
    database = SQLiteDatabase(":memory:")

    database.initialize()

    connection = database.connect()

    columns = {
        row["name"]
        for row in connection.execute("""
            PRAGMA table_info(academic_classes)
        """).fetchall()
    }

    assert "tenant_id" in columns


def test_initialize_enables_foreign_keys():
    database = SQLiteDatabase(":memory:")

    database.initialize()

    connection = database.connect()

    foreign_keys = connection.execute("""
        PRAGMA foreign_keys
    """).fetchone()[0]

    assert foreign_keys == 1


def test_initialize_refuses_existing_database_without_history(tmp_path):
    database = SQLiteDatabase(tmp_path / "ambiguous.db")
    _create_ambiguous_legacy_database(database)

    try:
        database.initialize()
    except RuntimeError as error:
        assert "schema_migrations" in str(error)
    else:
        raise AssertionError("Une base historique ambiguë devait être refusée")

    connection = database.connect()
    row = connection.execute(
        "SELECT first_name, tenant_id FROM students WHERE id = ?",
        ("student-1",),
    ).fetchone()

    assert tuple(row) == ("Isaac", None)
    assert connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = 'schema_migrations'
        """
    ).fetchone() is None


def test_initialize_refuses_existing_database_with_empty_history(tmp_path):
    database = SQLiteDatabase(tmp_path / "empty-history.db")
    _create_ambiguous_legacy_database(database)
    connection = database.connect()
    connection.execute(
        """
        CREATE TABLE schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    connection.commit()

    with pytest.raises(RuntimeError, match="schema_migrations"):
        database.initialize()

    row = connection.execute(
        "SELECT first_name, tenant_id FROM students WHERE id = ?",
        ("student-1",),
    ).fetchone()
    assert tuple(row) == ("Isaac", None)


def test_initialize_still_creates_a_new_database(tmp_path):
    database = SQLiteDatabase(tmp_path / "new.db")

    database.initialize()

    connection = database.connect()
    assert connection.execute(
        "SELECT 1 FROM schema_migrations WHERE version = '018'"
    ).fetchone() is not None
