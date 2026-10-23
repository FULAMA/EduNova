from sqlite3 import Connection


version = "016"


def _has_tenant_scoped_primary_key(connection: Connection) -> bool:
    columns = connection.execute(
        "PRAGMA table_info(student_academic_records)"
    ).fetchall()
    primary_key = [
        column[1]
        for column in sorted(columns, key=lambda column: column[5])
        if column[5] > 0
    ]
    return primary_key == [
        "tenant_id",
        "student_id",
        "academic_period_id",
    ]


def upgrade(connection: Connection) -> None:
    if _has_tenant_scoped_primary_key(connection):
        return

    foreign_keys_enabled = connection.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]
    connection.execute("PRAGMA foreign_keys = OFF")
    savepoint = "edunova_migration_016"
    connection.execute(f"SAVEPOINT {savepoint}")

    try:
        connection.execute(
            """
            CREATE TABLE student_academic_records_new (
                tenant_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                academic_period_id TEXT NOT NULL,
                general_average REAL NOT NULL,
                failed_subjects INTEGER NOT NULL,
                credits_obtained REAL NOT NULL,
                total_credits REAL NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'DRAFT',

                PRIMARY KEY (
                    tenant_id,
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
            """
        )

        connection.execute(
            """
            INSERT INTO student_academic_records_new (
                tenant_id,
                student_id,
                academic_period_id,
                general_average,
                failed_subjects,
                credits_obtained,
                total_credits,
                version,
                status
            )
            SELECT
                tenant_id,
                student_id,
                academic_period_id,
                general_average,
                failed_subjects,
                credits_obtained,
                total_credits,
                COALESCE(version, 1),
                COALESCE(status, 'DRAFT')
            FROM student_academic_records
            """
        )

        connection.execute("DROP TABLE student_academic_records")
        connection.execute(
            "ALTER TABLE student_academic_records_new "
            "RENAME TO student_academic_records"
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            uq_student_academic_records_tenant_student_period
            ON student_academic_records (
                tenant_id,
                student_id,
                academic_period_id
            )
            """
        )
    except Exception:
        connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
        connection.execute(f"RELEASE SAVEPOINT {savepoint}")
        raise
    else:
        connection.execute(f"RELEASE SAVEPOINT {savepoint}")
    finally:
        connection.execute(
            "PRAGMA foreign_keys = "
            + ("ON" if foreign_keys_enabled else "OFF")
        )
