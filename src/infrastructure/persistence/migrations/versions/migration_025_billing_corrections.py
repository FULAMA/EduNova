from sqlite3 import Connection


version = "025"


def upgrade(connection: Connection) -> None:
    connection.execute("ALTER TABLE billing_receipts ADD COLUMN status TEXT NOT NULL DEFAULT 'ISSUED' CHECK (status IN ('ISSUED', 'REVERSED'))")
    connection.execute("ALTER TABLE billing_receipts ADD COLUMN reversed_by_entry_id TEXT")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS billing_counter_entries (
            id TEXT NOT NULL, tenant_id TEXT NOT NULL, original_payment_id TEXT NOT NULL,
            amount TEXT NOT NULL CHECK (CAST(amount AS DECIMAL) > 0),
            currency TEXT NOT NULL CHECK (currency IN ('USD', 'CDF')), reason TEXT NOT NULL,
            recorded_by TEXT NOT NULL, recorded_at TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id), UNIQUE (tenant_id, original_payment_id),
            FOREIGN KEY (tenant_id, original_payment_id) REFERENCES billing_payments (tenant_id, id)
        )
    """)
