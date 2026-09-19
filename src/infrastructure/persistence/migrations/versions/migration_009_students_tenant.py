from sqlite3 import Connection


version = "009"


def _has_tenant_id_column(connection: Connection) -> bool:
    columns = connection.execute("""
        PRAGMA table_info(students)
    """).fetchall()

    return any(column[1] == "tenant_id" for column in columns)


def _has_legacy_rows_without_tenant(connection: Connection) -> bool:
    if not _has_tenant_id_column(connection):
        row = connection.execute("""
            SELECT 1
            FROM students
            LIMIT 1
        """).fetchone()

        return row is not None

    row = connection.execute("""
        SELECT 1
        FROM students
        WHERE tenant_id IS NULL
        LIMIT 1
    """).fetchone()

    return row is not None


def upgrade(connection: Connection) -> None:
    if _has_legacy_rows_without_tenant(connection):
        raise RuntimeError(
            "Migration 009 impossible : des étudiants existants "
            "n'ont pas de tenant_id. Aucune donnée n'a été supprimée."
        )

    connection.execute("""
        CREATE TABLE students_new (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            active INTEGER NOT NULL
        )
    """)

    if _has_tenant_id_column(connection):
        connection.execute("""
            INSERT INTO students_new (
                id,
                tenant_id,
                first_name,
                last_name,
                email,
                phone,
                active
            )
            SELECT
                id,
                tenant_id,
                first_name,
                last_name,
                email,
                phone,
                active
            FROM students
        """)

    connection.execute("""
        DROP TABLE students
    """)

    connection.execute("""
        ALTER TABLE students_new
        RENAME TO students
    """)
