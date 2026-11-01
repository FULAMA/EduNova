import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import migration_039_academic_calendars


def create_periods_table(connection: sqlite3.Connection) -> None:
    connection.execute("""
        CREATE TABLE academic_periods (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            academic_year_id TEXT
        )
    """)


def insert_calendar(connection: sqlite3.Connection, calendar_id: str, tenant_id: str, name: str) -> None:
    connection.execute(
        "INSERT INTO academic_calendars (id, tenant_id, name) VALUES (?, ?, ?)",
        (calendar_id, tenant_id, name),
    )


def insert_period(
    connection: sqlite3.Connection,
    period_id: str,
    tenant_id: str,
    calendar_id: str | None,
    start_date: str,
    end_date: str,
) -> None:
    connection.execute(
        """
        INSERT INTO academic_periods
            (id, tenant_id, name, start_date, end_date, academic_calendar_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (period_id, tenant_id, period_id, start_date, end_date, calendar_id),
    )


def test_migration_is_idempotent_and_preserves_unclassified_legacy_periods():
    connection = sqlite3.connect(":memory:")
    create_periods_table(connection)
    connection.execute(
        """
        INSERT INTO academic_periods
            (id, tenant_id, name, start_date, end_date, academic_year_id)
        VALUES ('legacy', 'tenant-a', 'Legacy period', '2026-09-01', '2026-12-20', NULL)
        """
    )

    migration_039_academic_calendars.upgrade(connection)
    migration_039_academic_calendars.upgrade(connection)

    row = connection.execute(
        "SELECT academic_calendar_id FROM academic_periods WHERE id = 'legacy'"
    ).fetchone()
    assert row == (None,)
    assert connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type = 'trigger' AND name LIKE 'trg_academic_period_calendar_%'"
    ).fetchone()[0] == 4


def test_migration_rejects_overlap_inside_calendar_but_allows_other_calendars():
    connection = sqlite3.connect(":memory:")
    create_periods_table(connection)
    migration_039_academic_calendars.upgrade(connection)
    insert_calendar(connection, "calendar-a", "tenant-a", "Primary")
    insert_calendar(connection, "calendar-b", "tenant-a", "Secondary")

    insert_period(connection, "p1", "tenant-a", "calendar-a", "2026-09-01", "2026-12-20")
    with pytest.raises(sqlite3.IntegrityError, match="cannot overlap"):
        insert_period(connection, "p2", "tenant-a", "calendar-a", "2026-12-20", "2027-02-01")

    insert_period(connection, "p3", "tenant-a", "calendar-b", "2026-10-01", "2027-01-15")
    assert connection.execute("SELECT COUNT(*) FROM academic_periods").fetchone()[0] == 2


def test_migration_rejects_calendar_reference_from_another_tenant():
    connection = sqlite3.connect(":memory:")
    create_periods_table(connection)
    migration_039_academic_calendars.upgrade(connection)
    insert_calendar(connection, "calendar-a", "tenant-a", "Primary")

    with pytest.raises(sqlite3.IntegrityError, match="same tenant"):
        insert_period(connection, "cross-tenant", "tenant-b", "calendar-a", "2026-09-01", "2026-12-20")
