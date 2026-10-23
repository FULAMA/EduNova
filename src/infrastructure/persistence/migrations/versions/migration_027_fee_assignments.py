from sqlite3 import Connection


version = "027"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS billing_fee_assignments (
            id TEXT NOT NULL, tenant_id TEXT NOT NULL, fee_type_id TEXT NOT NULL,
            fee_type_version INTEGER NOT NULL, student_id TEXT NOT NULL,
            academic_period_id TEXT, charge_id TEXT NOT NULL, created_by TEXT NOT NULL,
            created_at TEXT NOT NULL, PRIMARY KEY (tenant_id, id),
            UNIQUE (tenant_id, fee_type_id, student_id, academic_period_id),
            UNIQUE (tenant_id, charge_id),
            FOREIGN KEY (tenant_id, fee_type_id) REFERENCES billing_fee_types (tenant_id, id),
            FOREIGN KEY (tenant_id, student_id) REFERENCES students (tenant_id, id),
            FOREIGN KEY (tenant_id, charge_id) REFERENCES billing_charges (tenant_id, id)
        )
    """)
