from sqlite3 import Connection


version = "022"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS attendance_records (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            academic_class_id TEXT NOT NULL,
            academic_year_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('PRESENT', 'ABSENT', 'LATE')),
            justified INTEGER NOT NULL CHECK (justified IN (0, 1)),
            recorded_by TEXT,
            version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
            PRIMARY KEY (tenant_id, id),
            UNIQUE (tenant_id, student_id, attendance_date),
            FOREIGN KEY (tenant_id, student_id) REFERENCES students (tenant_id, id),
            FOREIGN KEY (tenant_id, academic_class_id) REFERENCES academic_classes (tenant_id, id),
            FOREIGN KEY (tenant_id, academic_year_id) REFERENCES academic_years (tenant_id, id),
            FOREIGN KEY (tenant_id, academic_period_id) REFERENCES academic_periods (tenant_id, id),
            CHECK (status != 'PRESENT' OR justified = 0)
        )
    """)
    connection.execute("""
        CREATE INDEX IF NOT EXISTS ix_attendance_lookup
        ON attendance_records (tenant_id, academic_class_id, academic_period_id, attendance_date)
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS attendance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            attendance_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            previous_status TEXT,
            previous_justified INTEGER,
            new_status TEXT NOT NULL,
            new_justified INTEGER NOT NULL,
            changed_by TEXT NOT NULL,
            changed_at TEXT NOT NULL,
            UNIQUE (tenant_id, attendance_id, version),
            FOREIGN KEY (tenant_id, attendance_id)
                REFERENCES attendance_records (tenant_id, id) ON DELETE CASCADE
        )
    """)
