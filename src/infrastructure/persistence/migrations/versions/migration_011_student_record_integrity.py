from sqlite3 import Connection

version = "011"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_students_tenant_id
        ON students (tenant_id, id)
    """)

    connection.execute("PRAGMA foreign_keys = OFF")

    connection.execute("""
        CREATE TABLE student_academic_records_new (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            general_average REAL NOT NULL,
            failed_subjects INTEGER NOT NULL,
            credits_obtained REAL NOT NULL,
            total_credits REAL NOT NULL,

            PRIMARY KEY (
                student_id,
                academic_period_id
            ),

            FOREIGN KEY (
                tenant_id,
                student_id
            )
            REFERENCES students (
                tenant_id,
                id
            )
        )
    """)

    connection.execute("""
        INSERT INTO student_academic_records_new (
            student_id,
            academic_period_id,
            tenant_id,
            general_average,
            failed_subjects,
            credits_obtained,
            total_credits
        )
        SELECT
            student_id,
            academic_period_id,
            tenant_id,
            general_average,
            failed_subjects,
            credits_obtained,
            total_credits
        FROM student_academic_records
    """)

    connection.execute(
        "DROP TABLE student_academic_records"
    )

    connection.execute("""
        ALTER TABLE student_academic_records_new
        RENAME TO student_academic_records
    """)

    connection.execute("PRAGMA foreign_keys = ON")
