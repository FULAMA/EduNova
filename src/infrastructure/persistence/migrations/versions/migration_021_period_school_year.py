from sqlite3 import Connection


version = "021"


def upgrade(connection: Connection) -> None:
    columns = connection.execute("PRAGMA table_info(academic_periods)").fetchall()
    if not any(column[1] == "academic_year_id" for column in columns):
        # NULL is intentionally retained for historical rows: no year is inferred.
        connection.execute("ALTER TABLE academic_periods ADD COLUMN academic_year_id TEXT")

    connection.execute("""
        CREATE INDEX IF NOT EXISTS ix_academic_period_year_lookup
        ON academic_periods (tenant_id, academic_year_id, start_date)
    """)
    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_academic_period_name_per_year
        ON academic_periods (tenant_id, academic_year_id, name COLLATE NOCASE)
        WHERE academic_year_id IS NOT NULL
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_academic_period_year_tenant_insert
        BEFORE INSERT ON academic_periods
        WHEN NEW.academic_year_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM academic_years
            WHERE tenant_id = NEW.tenant_id AND id = NEW.academic_year_id
        )
        BEGIN
            SELECT RAISE(ABORT, 'academic period year must belong to the same tenant');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_academic_period_year_tenant_update
        BEFORE UPDATE OF tenant_id, academic_year_id ON academic_periods
        WHEN NEW.academic_year_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM academic_years
            WHERE tenant_id = NEW.tenant_id AND id = NEW.academic_year_id
        )
        BEGIN
            SELECT RAISE(ABORT, 'academic period year must belong to the same tenant');
        END
    """)
