from sqlite3 import Connection


version = "031"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS report_cards (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            deliberation_id TEXT NOT NULL,
            deliberation_version INTEGER NOT NULL CHECK (deliberation_version > 0),
            record_version INTEGER NOT NULL CHECK (record_version > 0),
            report_version INTEGER NOT NULL CHECK (report_version > 0),
            status TEXT NOT NULL CHECK (status IN ('DRAFT', 'ISSUED', 'SUPERSEDED')),
            snapshot_json TEXT NOT NULL,
            snapshot_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            issued_at TEXT,
            issued_by TEXT,
            previous_report_card_id TEXT,
            PRIMARY KEY (tenant_id, id),
            UNIQUE (tenant_id, student_id, academic_period_id, report_version),
            FOREIGN KEY (tenant_id, student_id) REFERENCES students (tenant_id, id),
            FOREIGN KEY (tenant_id, academic_period_id) REFERENCES academic_periods (tenant_id, id),
            FOREIGN KEY (tenant_id, deliberation_id) REFERENCES academic_deliberations (tenant_id, id)
        )
    """)
