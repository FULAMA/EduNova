from sqlite3 import Connection


version = "020"


def upgrade(connection: Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS academic_years (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            label TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id),
            UNIQUE (tenant_id, label)
        )
        """
    )
    connection.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_academic_year_active
        ON academic_years (tenant_id)
        WHERE status = 'ACTIVE'
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS student_assignments (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            academic_year_id TEXT NOT NULL,
            academic_class_id TEXT NOT NULL,
            academic_option_id TEXT,
            status TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            closed_at TEXT,
            PRIMARY KEY (tenant_id, id),
            FOREIGN KEY (tenant_id, student_id)
                REFERENCES students (tenant_id, id),
            FOREIGN KEY (tenant_id, academic_year_id)
                REFERENCES academic_years (tenant_id, id),
            FOREIGN KEY (tenant_id, academic_class_id)
                REFERENCES academic_classes (tenant_id, id),
            FOREIGN KEY (tenant_id, academic_option_id)
                REFERENCES academic_options (tenant_id, id)
        )
        """
    )
    connection.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_student_assignment_active
        ON student_assignments (tenant_id, student_id, academic_year_id)
        WHERE status = 'ACTIVE'
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_student_assignments_lookup
        ON student_assignments (tenant_id, student_id, academic_year_id, created_at)
        """
    )
