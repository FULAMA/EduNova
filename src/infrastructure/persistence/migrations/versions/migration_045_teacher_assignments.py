from sqlite3 import Connection


version = "045"


def upgrade(connection: Connection) -> None:
    """Affectations des enseignants (Lot 7).

    Permet de rattacher un enseignant à une classe et une matière pour une année scolaire :
    - Clé primaire composite (tenant_id, teacher_user_id, academic_class_id, subject_id, academic_year_id).
    - Traçabilité de l'administrateur ayant effectué l'affectation.
    - Index pour requêtes par enseignant et par classe/matière.
    """
    connection.execute("""
        CREATE TABLE IF NOT EXISTS teacher_assignments (
            tenant_id TEXT NOT NULL,
            teacher_user_id TEXT NOT NULL,
            academic_class_id TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            academic_year_id TEXT NOT NULL,
            assigned_by TEXT NOT NULL,
            assigned_at TEXT NOT NULL,
            PRIMARY KEY (tenant_id, teacher_user_id, academic_class_id, subject_id, academic_year_id),
            FOREIGN KEY (tenant_id) REFERENCES tenants (id),
            FOREIGN KEY (teacher_user_id) REFERENCES users (id),
            FOREIGN KEY (assigned_by) REFERENCES users (id),
            FOREIGN KEY (tenant_id, academic_class_id) REFERENCES academic_classes (tenant_id, id),
            FOREIGN KEY (tenant_id, subject_id) REFERENCES subjects (tenant_id, id),
            FOREIGN KEY (tenant_id, academic_year_id) REFERENCES academic_years (tenant_id, id)
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_teacher_assignments_lookup
        ON teacher_assignments (tenant_id, teacher_user_id, academic_year_id)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_teacher_assignments_class_subject
        ON teacher_assignments (tenant_id, academic_class_id, subject_id)
    """)
