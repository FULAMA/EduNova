from sqlite3 import Connection


version = "005"


def _has_tenant_id_column(connection: Connection) -> bool:
    columns = connection.execute("""
        PRAGMA table_info(class_options)
    """).fetchall()

    return any(column[1] == "tenant_id" for column in columns)


def _has_legacy_rows_without_tenant(connection: Connection) -> bool:
    if not _has_tenant_id_column(connection):
        row = connection.execute("""
            SELECT 1
            FROM class_options
            LIMIT 1
        """).fetchone()

        return row is not None

    row = connection.execute("""
        SELECT 1
        FROM class_options
        WHERE tenant_id IS NULL
        LIMIT 1
    """).fetchone()

    return row is not None


def upgrade(connection: Connection) -> None:
    if _has_legacy_rows_without_tenant(connection):
        raise RuntimeError(
            "Migration 005 impossible : des associations "
            "classe-option existantes n'ont pas de tenant_id. "
            "Aucune donnée n'a été supprimée."
        )

    connection.execute("""
        CREATE TABLE class_options_new (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            academic_class_id TEXT NOT NULL,
            academic_option_id TEXT NOT NULL,
            active INTEGER NOT NULL,
            UNIQUE (
                academic_class_id,
                academic_option_id
            )
        )
    """)

    if _has_tenant_id_column(connection):
        connection.execute("""
            INSERT INTO class_options_new (
                id,
                tenant_id,
                academic_class_id,
                academic_option_id,
                active
            )
            SELECT
                id,
                tenant_id,
                academic_class_id,
                academic_option_id,
                active
            FROM class_options
        """)

    connection.execute("""
        DROP TABLE class_options
    """)

    connection.execute("""
        ALTER TABLE class_options_new
        RENAME TO class_options
    """)
