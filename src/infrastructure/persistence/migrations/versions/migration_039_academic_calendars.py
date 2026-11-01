from sqlite3 import Connection


version = "039"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS academic_calendars (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL CHECK (length(trim(name)) > 0),
            description TEXT,
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
            UNIQUE (tenant_id, id),
            UNIQUE (tenant_id, name COLLATE NOCASE)
        )
    """)
    connection.execute("""
        CREATE INDEX IF NOT EXISTS ix_academic_calendars_tenant_active
        ON academic_calendars (tenant_id, is_active, name COLLATE NOCASE)
    """)

    columns = connection.execute(
        "PRAGMA table_info(academic_periods)"
    ).fetchall()
    if not any(column[1] == "academic_calendar_id" for column in columns):
        # Existing periods remain unclassified; no calendar is inferred.
        connection.execute(
            "ALTER TABLE academic_periods ADD COLUMN academic_calendar_id TEXT"
        )

    connection.execute("""
        CREATE INDEX IF NOT EXISTS ix_academic_period_calendar_dates
        ON academic_periods
            (tenant_id, academic_calendar_id, start_date, end_date)
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_academic_period_calendar_tenant_insert
        BEFORE INSERT ON academic_periods
        WHEN NEW.academic_calendar_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM academic_calendars
            WHERE tenant_id = NEW.tenant_id
              AND id = NEW.academic_calendar_id
        )
        BEGIN
            SELECT RAISE(ABORT, 'academic period calendar must belong to the same tenant');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_academic_period_calendar_tenant_update
        BEFORE UPDATE OF tenant_id, academic_calendar_id ON academic_periods
        WHEN NEW.academic_calendar_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM academic_calendars
            WHERE tenant_id = NEW.tenant_id
              AND id = NEW.academic_calendar_id
        )
        BEGIN
            SELECT RAISE(ABORT, 'academic period calendar must belong to the same tenant');
        END
    """)

    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_academic_period_calendar_no_overlap_insert
        BEFORE INSERT ON academic_periods
        WHEN NEW.academic_calendar_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM academic_periods existing
            WHERE existing.tenant_id = NEW.tenant_id
              AND existing.academic_calendar_id = NEW.academic_calendar_id
              AND NEW.start_date <= existing.end_date
              AND existing.start_date <= NEW.end_date
        )
        BEGIN
            SELECT RAISE(ABORT, 'academic periods cannot overlap within the same calendar');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_academic_period_calendar_no_overlap_update
        BEFORE UPDATE OF tenant_id, academic_calendar_id, start_date, end_date
        ON academic_periods
        WHEN NEW.academic_calendar_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM academic_periods existing
            WHERE existing.id <> NEW.id
              AND existing.tenant_id = NEW.tenant_id
              AND existing.academic_calendar_id = NEW.academic_calendar_id
              AND NEW.start_date <= existing.end_date
              AND existing.start_date <= NEW.end_date
        )
        BEGIN
            SELECT RAISE(ABORT, 'academic periods cannot overlap within the same calendar');
        END
    """)
