from sqlite3 import Connection


version = "041"


def upgrade(connection: Connection) -> None:
    """Suivi persistant des relances et rappels d'impayés (Décision 22).

    Permet d'auditer et d'historiser les rappels adressés aux parents/responsables
    pour les créances impayées, sans application automatique de pénalité.
    """
    connection.execute("""
        CREATE TABLE IF NOT EXISTS billing_fee_reminders (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            charge_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            channel TEXT NOT NULL CHECK (channel IN ('SMS', 'EMAIL', 'LETTER', 'PHONE', 'IN_PERSON')),
            recipient TEXT NOT NULL,
            notes TEXT,
            sent_at TEXT NOT NULL,
            sent_by TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id),
            FOREIGN KEY (tenant_id, charge_id)
                REFERENCES billing_charges (tenant_id, id),
            FOREIGN KEY (tenant_id, student_id)
                REFERENCES students (tenant_id, id)
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_billing_fee_reminders_charge
        ON billing_fee_reminders (tenant_id, charge_id)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_billing_fee_reminders_student
        ON billing_fee_reminders (tenant_id, student_id)
    """)
