from sqlite3 import Connection


version = "002"


def _has_tenant_id_column(connection: Connection) -> bool:
    columns = connection.execute("""
        PRAGMA table_info(academic_classes)
    """).fetchall()

    return any(column[1] == "tenant_id" for column in columns)


def _has_legacy_rows_without_tenant(connection: Connection) -> bool:
    if not _has_tenant_id_column(connection):
        row = connection.execute("""
            SELECT 1
            FROM academic_classes
            LIMIT 1
        """).fetchone()

        return row is not None

    row = connection.execute("""
        SELECT 1
        FROM academic_classes
        WHERE tenant_id IS NULL
        LIMIT 1
    """).fetchone()

    return row is not None


def upgrade(connection: Connection) -> None:
    if _has_legacy_rows_without_tenant(connection):
        raise RuntimeError(
            "Migration 002 impossible : des classes existantes "
            "n'ont pas de tenant_id. Aucune donnée n'a été supprimée."
        )

    connection.execute("""
        CREATE TABLE academic_classes_new (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL
        )
    """)

    if _has_tenant_id_column(connection):
        connection.execute("""
            INSERT INTO academic_classes_new (
                id,
                tenant_id,
                name
            )
            SELECT
                id,
                tenant_id,
                name
            FROM academic_classes
        """)

    connection.execute("""
        DROP TABLE academic_classes
    """)

    connection.execute("""
        ALTER TABLE academic_classes_new
        RENAME TO academic_classes
    """)
