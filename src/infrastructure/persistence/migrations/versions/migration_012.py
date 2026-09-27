from sqlite3 import Connection

version = "012"


def upgrade(connection: Connection) -> None:
    table_exists = connection.execute("""
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'subject_results'
    """).fetchone()

    if table_exists is None:
        return

    orphan_count = connection.execute("""
        SELECT COUNT(*)
        FROM subject_results sr
        LEFT JOIN student_academic_records sar
          ON sar.student_id = sr.student_id
         AND sar.academic_period_id = sr.academic_period_id
        WHERE sar.student_id IS NULL
    """).fetchone()[0]

    if orphan_count > 0:
        raise ValueError(
            "Des subject_results orphelins existent et ne peuvent pas "
            "etre rattaches a un dossier academique."
        )

    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        uq_student_academic_records_tenant_student_period
        ON student_academic_records (
            tenant_id,
            student_id,
            academic_period_id
        )
    """)

    connection.execute("PRAGMA foreign_keys = OFF")

    connection.execute("""
        CREATE TABLE subject_results_new (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            average REAL NOT NULL,
            coefficient REAL NOT NULL,
            position INTEGER NOT NULL,

            FOREIGN KEY (
                tenant_id,
                student_id,
                academic_period_id
            )
            REFERENCES student_academic_records (
                tenant_id,
                student_id,
                academic_period_id
            )
        )
    """)

    connection.execute("""
        INSERT INTO subject_results_new (
            student_id,
            academic_period_id,
            tenant_id,
            subject_id,
            average,
            coefficient,
            position
        )
        SELECT
            sr.student_id,
            sr.academic_period_id,
            sar.tenant_id,
            sr.subject_id,
            sr.average,
            sr.coefficient,
            sr.position
        FROM subject_results sr
        JOIN student_academic_records sar
          ON sar.student_id = sr.student_id
         AND sar.academic_period_id = sr.academic_period_id
    """)

    connection.execute("DROP TABLE subject_results")

    connection.execute("""
        ALTER TABLE subject_results_new
        RENAME TO subject_results
    """)

    connection.execute("PRAGMA foreign_keys = ON")
