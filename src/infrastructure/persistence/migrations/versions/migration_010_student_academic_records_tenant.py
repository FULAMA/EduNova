from sqlite3 import Connection

version = "010"


def _has_tenant_id_column(connection: Connection) -> bool:
    columns = connection.execute("""
        PRAGMA table_info(student_academic_records)
    """).fetchall()

    return any(column[1] == "tenant_id" for column in columns)


def _has_legacy_rows_without_tenant(connection: Connection) -> bool:
    if not _has_tenant_id_column(connection):
        row = connection.execute("""
            SELECT 1
            FROM student_academic_records
            LIMIT 1
        """).fetchone()

        return row is not None

    row = connection.execute("""
        SELECT 1
        FROM student_academic_records
        WHERE tenant_id IS NULL
        LIMIT 1
    """).fetchone()

    return row is not None


def upgrade(connection: Connection) -> None:
    if _has_legacy_rows_without_tenant(connection):
        raise RuntimeError(
            "Migration 010 impossible : des dossiers académiques "
            "existants n'ont pas de tenant_id. "
            "Aucune donnée n'a été supprimée."
        )

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
            )
        )
    """)

    if _has_tenant_id_column(connection):
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

    connection.execute("""
        DROP TABLE student_academic_records
    """)

    connection.execute("""
        ALTER TABLE student_academic_records_new
        RENAME TO student_academic_records
    """)
