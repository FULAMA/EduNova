import sqlite3

import pytest

from src.infrastructure.persistence.migrations.migration import Migration
from src.infrastructure.persistence.migrations.runner import MigrationRunner


def test_runner_creates_migration_history_table():
    connection = sqlite3.connect(":memory:")

    runner = MigrationRunner(connection)

    runner.run()

    row = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'schema_migrations'
    """).fetchone()

    assert row is not None


def test_runner_does_not_duplicate_migration_history():
    connection = sqlite3.connect(":memory:")

    runner = MigrationRunner(connection)

    runner.run()
    runner.run()

    rows = connection.execute("""
        SELECT version
        FROM schema_migrations
    """).fetchall()

    assert len(rows) == 0


def test_runner_applies_registered_migration():
    connection = sqlite3.connect(":memory:")

    runner = MigrationRunner(connection)

    runner.register(
        "001",
        lambda connection: connection.execute("""
            CREATE TABLE test_migration (
                id INTEGER PRIMARY KEY
            )
        """),
    )

    runner.run()

    table = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'test_migration'
    """).fetchone()

    migration = connection.execute("""
        SELECT version
        FROM schema_migrations
        WHERE version = '001'
    """).fetchone()

    assert table is not None
    assert migration is not None


def test_runner_executes_migration_only_once():
    connection = sqlite3.connect(":memory:")

    runner = MigrationRunner(connection)

    execution_count = 0

    def migration(connection):
        nonlocal execution_count
        execution_count += 1

    runner.register("001", migration)

    runner.run()
    runner.run()

    assert execution_count == 1

    rows = connection.execute("""
        SELECT version
        FROM schema_migrations
        WHERE version = '001'
    """).fetchall()

    assert len(rows) == 1


def test_runner_applies_migrations_in_version_order():
    connection = sqlite3.connect(":memory:")

    runner = MigrationRunner(connection)

    execution_order = []

    runner.register(
        "003",
        lambda connection: execution_order.append("003"),
    )

    runner.register(
        "001",
        lambda connection: execution_order.append("001"),
    )

    runner.register(
        "002",
        lambda connection: execution_order.append("002"),
    )

    runner.run()

    assert execution_order == ["001", "002", "003"]


def test_runner_accepts_migration_module():
    connection = sqlite3.connect(":memory:")

    runner = MigrationRunner(connection)

    runner.register_module(
        type(
            "Migration",
            (),
            {
                "version": "001",
                "upgrade": staticmethod(
                    lambda connection: connection.execute("""
                        CREATE TABLE module_migration (
                            id INTEGER PRIMARY KEY
                        )
                    """)
                ),
            },
        )
    )

    runner.run()

    table = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'module_migration'
    """).fetchone()

    assert table is not None


def test_migration_contract_requires_version_and_upgrade():
    migration = Migration(
        version="001",
        upgrade=lambda connection: None,
    )

    assert migration.version == "001"
    assert callable(migration.upgrade)


def test_runner_registers_migration_object():
    connection = sqlite3.connect(":memory:")

    runner = MigrationRunner(connection)

    migration = Migration(
        version="001",
        upgrade=lambda connection: connection.execute("""
            CREATE TABLE object_migration (
                id INTEGER PRIMARY KEY
            )
        """),
    )

    runner.register(migration)

    runner.run()

    table = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'object_migration'
    """).fetchone()

    assert table is not None
def test_migration_rejects_empty_version():
    with pytest.raises(ValueError):
        Migration(
            version="",
            upgrade=lambda connection: None,
        )


def test_migration_rejects_non_callable_upgrade():
    with pytest.raises(TypeError):
        Migration(
            version="001",
            upgrade=None,
        )
def test_runner_can_load_migration_from_versions_package():
    connection = sqlite3.connect(":memory:")

    runner = MigrationRunner(connection)

    from src.infrastructure.persistence.migrations.versions import (
        migration_001_baseline,
    )

    runner.register_module(migration_001_baseline)
    runner.run()

    migration = connection.execute("""
        SELECT version
        FROM schema_migrations
        WHERE version = '001'
    """).fetchone()

    assert migration is not None
def test_runner_records_applied_at_for_migration():
    connection = sqlite3.connect(":memory:")

    runner = MigrationRunner(connection)

    from src.infrastructure.persistence.migrations.versions import (
        migration_001_baseline,
    )

    runner.register_module(migration_001_baseline)
    runner.run()

    row = connection.execute("""
        SELECT version, applied_at
        FROM schema_migrations
        WHERE version = '001'
    """).fetchone()

    assert row is not None
    assert row["version"] == "001"
    assert row["applied_at"]

def test_runner_discovers_migrations_from_versions_package():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    runner = MigrationRunner(connection)

    runner.discover(
        "src.infrastructure.persistence.migrations.versions"
    )

    runner.run()

    row = connection.execute("""
        SELECT version
        FROM schema_migrations
        WHERE version = '001'
    """).fetchone()

    assert row is not None
    assert row["version"] == "001"


def test_runner_records_applied_at_for_migration():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    runner = MigrationRunner(connection)

    from src.infrastructure.persistence.migrations.versions import (
        migration_001_baseline,
    )

    runner.register_module(migration_001_baseline)
    runner.run()

    row = connection.execute("""
        SELECT version, applied_at
        FROM schema_migrations
        WHERE version = '001'
    """).fetchone()

    assert row is not None
    assert row["version"] == "001"
    assert row["applied_at"]
def test_runner_discovers_migrations_from_versions_package():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    runner = MigrationRunner(connection)

    runner.discover(
        "src.infrastructure.persistence.migrations.versions"
    )

    runner.run()

    row = connection.execute("""
        SELECT version
        FROM schema_migrations
        WHERE version = '001'
    """).fetchone()

    assert row is not None
    assert row["version"] == "001"
def test_runner_ignores_modules_without_migration_contract():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    runner = MigrationRunner(connection)

    runner.discover(
        "src.infrastructure.persistence.migrations.versions"
    )

    assert "001" in runner._migrations
