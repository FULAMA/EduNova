from sqlite3 import Connection


version = "019"


def upgrade(connection: Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS student_academic_record_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            status TEXT NOT NULL,
            operation TEXT NOT NULL,
            snapshot_json TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (tenant_id, student_id)
                REFERENCES students (tenant_id, id)
                ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_student_academic_record_history_lookup
        ON student_academic_record_history (
            tenant_id, student_id, academic_period_id, id
        )
        """
    )
