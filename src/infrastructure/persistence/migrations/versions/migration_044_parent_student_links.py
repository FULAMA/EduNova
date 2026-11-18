from sqlite3 import Connection


version = "044"


def upgrade(connection: Connection) -> None:
    """Relations parent-élève (PAR-REL-01 à PAR-REL-06 — Lot 8).

    Modèle distinct de student_user_links avec cardinalité N:M :
    - Un parent peut avoir plusieurs enfants.
    - Un élève peut avoir plusieurs responsables légaux.
    """
    connection.execute("""
        CREATE TABLE IF NOT EXISTS parent_student_links (
            tenant_id TEXT NOT NULL,
            parent_user_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL CHECK (relationship_type IN ('FATHER', 'MOTHER', 'LEGAL_GUARDIAN')),
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (tenant_id, parent_user_id, student_id),
            FOREIGN KEY (parent_user_id) REFERENCES users (id),
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (tenant_id, student_id)
                REFERENCES students (tenant_id, id)
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_parent_student_links_parent
        ON parent_student_links (tenant_id, parent_user_id)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_parent_student_links_student
        ON parent_student_links (tenant_id, student_id)
    """)
