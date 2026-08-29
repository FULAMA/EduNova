import sqlite3
from pathlib import Path


class SQLiteDatabase:
    def __init__(self, database_path: str | Path):
        self._database_path = str(database_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
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