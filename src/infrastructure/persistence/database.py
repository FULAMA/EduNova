import sqlite3
from pathlib import Path

from src.infrastructure.persistence.migrations.runner import MigrationRunner


class SQLiteDatabase:
    def __init__(self, database_path: str | Path):
        self._database_path = str(database_path)
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        if self._database_path == ":memory:":
            if self._connection is None:
                self._connection = sqlite3.connect(
                    self._database_path,
                    check_same_thread=False,
                )
                self._connection.row_factory = sqlite3.Row
                self._connection.execute(
                    "PRAGMA foreign_keys = ON"
                )

            return self._connection

        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    def initialize(self) -> None:
        with self.connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS subjects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL UNIQUE,
                    coefficient REAL NOT NULL,
                    active INTEGER NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS academic_classes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS academic_options (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL UNIQUE,
                    active INTEGER NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS class_options (
                    id TEXT PRIMARY KEY,
                    academic_class_id TEXT NOT NULL,
                    academic_option_id TEXT NOT NULL,
                    active INTEGER NOT NULL,

                    UNIQUE (
                        academic_class_id,
                        academic_option_id
                    ),

                    FOREIGN KEY (academic_class_id)
                        REFERENCES academic_classes (id),

                    FOREIGN KEY (academic_option_id)
                        REFERENCES academic_options (id)
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS class_subjects (
                    id TEXT PRIMARY KEY,
                    academic_class_id TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    coefficient REAL NOT NULL,
                    academic_option_id TEXT,
                    active INTEGER NOT NULL,

                    UNIQUE (
                        academic_class_id,
                        subject_id,
                        academic_option_id
                    ),

                    FOREIGN KEY (academic_class_id)
                        REFERENCES academic_classes (id),

                    FOREIGN KEY (subject_id)
                        REFERENCES subjects (id),

                    FOREIGN KEY (academic_option_id)
                        REFERENCES academic_options (id)
                )
                """
            )

            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS
                uq_class_subject_common
                ON class_subjects (
                    academic_class_id,
                    subject_id
                )
                WHERE academic_option_id IS NULL
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_active INTEGER NOT NULL,
                    two_factor_enabled INTEGER NOT NULL,
                    two_factor_secret TEXT
                )
                """
            )


            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS revoked_refresh_tokens (
                    jti TEXT PRIMARY KEY,
                    revoked_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id TEXT PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    active INTEGER NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS student_academic_records (
                    student_id TEXT NOT NULL,
                    academic_period_id TEXT NOT NULL,
                    general_average REAL NOT NULL,
                    failed_subjects INTEGER NOT NULL,
                    credits_obtained REAL NOT NULL,
                    total_credits REAL NOT NULL,

                    PRIMARY KEY (
                        student_id,
                        academic_period_id
                    )
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS subject_results (
                    student_id TEXT NOT NULL,
                    academic_period_id TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    average REAL NOT NULL,
                    coefficient REAL NOT NULL,
                    position INTEGER NOT NULL,

                    PRIMARY KEY (
                        student_id,
                        academic_period_id,
                        subject_id
                    ),

                    FOREIGN KEY (
                        student_id,
                        academic_period_id
                    )
                    REFERENCES student_academic_records (
                        student_id,
                        academic_period_id
                    )
                    ON DELETE CASCADE
                )
                """
            )

            runner = MigrationRunner(connection)
            runner.discover(
                "src.infrastructure.persistence.migrations.versions"
            )
            runner.run()
