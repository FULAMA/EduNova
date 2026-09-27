from sqlite3 import Connection


version = "004"


def _has_tenant_id_column(connection: Connection) -> bool:
    columns = connection.execute("""
        PRAGMA table_info(academic_options)
    """).fetchall()

    return any(column[1] == "tenant_id" for column in columns)


def _has_legacy_rows_without_tenant(connection: Connection) -> bool:
    if not _has_tenant_id_column(connection):
        row = connection.execute("""
            SELECT 1
            FROM academic_options
            LIMIT 1
        """).fetchone()

        return row is not None

    row = connection.execute("""
        SELECT 1
        FROM academic_options
        WHERE tenant_id IS NULL
        LIMIT 1
    """).fetchone()

    return row is not None


def upgrade(connection: Connection) -> None:
    if _has_legacy_rows_without_tenant(connection):
        raise RuntimeError(
            "Migration 004 impossible : des options académiques existantes "
            "n'ont pas de tenant_id. Aucune donnée n'a été supprimée."
        )

    connection.execute("""
        CREATE TABLE academic_options_new (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            active INTEGER NOT NULL
        )
    """)

    if _has_tenant_id_column(connection):
        connection.execute("""
            INSERT INTO academic_options_new (
                id,
                tenant_id,
                name,
                code,
                active
            )
            SELECT
                id,
                tenant_id,
                name,
                code,
                active
            FROM academic_options
        """)

    connection.execute("""
        DROP TABLE academic_options
    """)

    connection.execute("""
        ALTER TABLE academic_options_new
        RENAME TO academic_options
    """)
