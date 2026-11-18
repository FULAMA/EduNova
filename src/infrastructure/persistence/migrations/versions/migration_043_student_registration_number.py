from sqlite3 import Connection


version = "043"


def upgrade(connection: Connection) -> None:
    """Option A de la Décision 45 : Matricule d'établissement optionnel et unique par tenant.

    Conserve l'UUID interne immuable, ajoute un identifiant/matricule d'école optionnel
    avec unicité stricte par tenant lorsqu'il est renseigné.
    """
    # Vérifier si la colonne existe déjà (pour idempotence)
    columns = [col[1] for col in connection.execute("PRAGMA table_info(students)").fetchall()]
    if "registration_number" not in columns:
        connection.execute("ALTER TABLE students ADD COLUMN registration_number TEXT")

    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_students_tenant_registration_number
        ON students (tenant_id, registration_number)
        WHERE registration_number IS NOT NULL
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_students_tenant_names
        ON students (tenant_id, last_name, first_name)
    """)
