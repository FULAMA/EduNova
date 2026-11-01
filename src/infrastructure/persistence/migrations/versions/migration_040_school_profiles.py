from sqlite3 import Connection


version = "040"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS school_profiles (
            tenant_id TEXT PRIMARY KEY,
            legal_name TEXT NOT NULL CHECK (length(trim(legal_name)) > 0),
            display_name TEXT NOT NULL CHECK (length(trim(display_name)) > 0),
            address TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            logo_url TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE RESTRICT
        )
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_school_profiles_updated_at
        AFTER UPDATE ON school_profiles
        FOR EACH ROW
        WHEN NEW.updated_at = OLD.updated_at
        BEGIN
            UPDATE school_profiles
            SET updated_at = CURRENT_TIMESTAMP
            WHERE tenant_id = NEW.tenant_id;
        END
    """)
