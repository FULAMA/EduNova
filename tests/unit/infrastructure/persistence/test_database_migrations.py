import sqlite3

from src.infrastructure.persistence.database import SQLiteDatabase


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
