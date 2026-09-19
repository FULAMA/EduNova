from sqlite3 import Connection


version = "003"


def _has_tenant_id_column(connection: Connection) -> bool:
    columns = connection.execute("""
        PRAGMA table_info(subjects)
    """).fetchall()

    return any(column[1] == "tenant_id" for column in columns)


def _has_legacy_rows_without_tenant(connection: Connection) -> bool:
    if not _has_tenant_id_column(connection):
        row = connection.execute("""
            SELECT 1
            FROM subjects
            LIMIT 1
        """).fetchone()

        return row is not None

    row = connection.execute("""
        SELECT 1
        FROM subjects
        WHERE tenant_id IS NULL
        LIMIT 1
    """).fetchone()

    return row is not None


def upgrade(connection: Connection) -> None:
    if _has_legacy_rows_without_tenant(connection):
        raise RuntimeError(
            "Migration 003 impossible : des matières existantes "
            "n'ont pas de tenant_id. Aucune donnée n'a été supprimée."
        )

    connection.execute("""
        CREATE TABLE subjects_new (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            coefficient REAL NOT NULL,
            active INTEGER NOT NULL
        )
    """)

    if _has_tenant_id_column(connection):
        connection.execute("""
            INSERT INTO subjects_new (
                id,
                tenant_id,
                name,
                code,
                coefficient,
                active
            )
            SELECT
                id,
                tenant_id,
                name,
                code,
                coefficient,
                active
            FROM subjects
        """)

    connection.execute("""
        DROP TABLE subjects
    """)

    connection.execute("""
        ALTER TABLE subjects_new
        RENAME TO subjects
    """)
