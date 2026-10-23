from sqlite3 import Connection


version = "028"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS academic_deliberations (
            id TEXT NOT NULL, tenant_id TEXT NOT NULL, student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL, record_version INTEGER NOT NULL,
            average REAL NOT NULL, failed_subjects INTEGER NOT NULL,
            decision TEXT NOT NULL CHECK (decision IN ('ADMITTED', 'CONDITIONAL', 'FAILED')),
            status TEXT NOT NULL CHECK (status IN ('PREPARED', 'VALIDATED', 'SUPERSEDED')),
            version INTEGER NOT NULL CHECK (version > 0), created_by TEXT NOT NULL,
            created_at TEXT NOT NULL, validated_by TEXT, validated_at TEXT,
            PRIMARY KEY (tenant_id, id),
            FOREIGN KEY (tenant_id, student_id) REFERENCES students (tenant_id, id),
            FOREIGN KEY (tenant_id, academic_period_id) REFERENCES academic_periods (tenant_id, id),
            UNIQUE (tenant_id, student_id, academic_period_id, record_version, version)
        )
    """)
