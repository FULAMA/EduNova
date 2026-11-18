from sqlite3 import Connection


version = "042"


def upgrade(connection: Connection) -> None:
    """Procédure formelle de contestation et réclamation de note (Décision 18).

    Permet la soumission, l'instruction sous examen, et la résolution motivée
    (acceptée ou rejetée) des réclamations de notes sans modification automatique
    de la note d'origine.
    """
    connection.execute("""
        CREATE TABLE IF NOT EXISTS academic_grade_disputes (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('SUBMITTED', 'UNDER_REVIEW', 'ACCEPTED', 'REJECTED')),
            submitted_by TEXT NOT NULL,
            submitted_at TEXT NOT NULL,
            reviewed_by TEXT,
            reviewed_at TEXT,
            resolution_notes TEXT,
            resolved_at TEXT,
            PRIMARY KEY (tenant_id, id),
            FOREIGN KEY (tenant_id, student_id)
                REFERENCES students (tenant_id, id),
            FOREIGN KEY (tenant_id, academic_period_id)
                REFERENCES academic_periods (tenant_id, id),
            FOREIGN KEY (tenant_id, subject_id)
                REFERENCES subjects (tenant_id, id)
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_academic_grade_disputes_student
        ON academic_grade_disputes (tenant_id, student_id)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_academic_grade_disputes_period
        ON academic_grade_disputes (tenant_id, academic_period_id)
    """)
