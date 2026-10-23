from sqlite3 import Connection


version = "026"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS billing_fee_types (
            id TEXT NOT NULL, tenant_id TEXT NOT NULL, name TEXT NOT NULL,
            description TEXT NOT NULL, category TEXT NOT NULL,
            amount TEXT NOT NULL CHECK (CAST(amount AS DECIMAL) > 0),
            currency TEXT NOT NULL CHECK (currency IN ('USD', 'CDF')),
            academic_period_id TEXT, applicability TEXT NOT NULL
                CHECK (applicability IN ('ESTABLISHMENT', 'CLASS', 'STUDENT')),
            status TEXT NOT NULL CHECK (status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')),
            version INTEGER NOT NULL CHECK (version > 0), created_by TEXT NOT NULL,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id), UNIQUE (tenant_id, name, version)
        )
    """)
