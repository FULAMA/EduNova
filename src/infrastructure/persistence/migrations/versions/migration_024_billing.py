from sqlite3 import Connection


version = "024"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS billing_charges (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            description TEXT NOT NULL,
            amount TEXT NOT NULL CHECK (CAST(amount AS DECIMAL) > 0),
            currency TEXT NOT NULL CHECK (currency IN ('USD', 'CDF')),
            due_date TEXT,
            status TEXT NOT NULL CHECK (status IN ('OPEN', 'CANCELLED')),
            PRIMARY KEY (tenant_id, id),
            FOREIGN KEY (tenant_id, student_id)
                REFERENCES students (tenant_id, id)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS billing_payments (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            charge_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            amount TEXT NOT NULL CHECK (CAST(amount AS DECIMAL) > 0),
            currency TEXT NOT NULL CHECK (currency IN ('USD', 'CDF')),
            idempotency_key TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('CONFIRMED', 'CANCELLED')),
            recorded_by TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            receipt_number TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id),
            UNIQUE (tenant_id, idempotency_key),
            UNIQUE (tenant_id, receipt_number),
            FOREIGN KEY (tenant_id, charge_id)
                REFERENCES billing_charges (tenant_id, id)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS billing_receipts (
            number TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            payment_id TEXT NOT NULL,
            amount TEXT NOT NULL,
            currency TEXT NOT NULL CHECK (currency IN ('USD', 'CDF')),
            issued_at TEXT NOT NULL,
            PRIMARY KEY (tenant_id, number),
            UNIQUE (tenant_id, payment_id),
            FOREIGN KEY (tenant_id, payment_id)
                REFERENCES billing_payments (tenant_id, id)
        )
    """)

