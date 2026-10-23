import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID, uuid4

import pytest

from src.academic.domain.entities.student_assignment import (
    StudentAssignmentStatus,
)
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_student_assignment_repository import (
    SQLiteStudentAssignmentRepository,
)


TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
OTHER_TENANT_ID = UUID("00000000-0000-0000-0000-000000000009")


class ClosingSQLiteDatabase(SQLiteDatabase):
    def connect(self):
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

        class ConnectionContext:
            def __enter__(self):
                return connection.__enter__()

            def __exit__(self, exc_type, exc_value, traceback):
                try:
                    return connection.__exit__(exc_type, exc_value, traceback)
                finally:
                    connection.close()

        return ConnectionContext()


def create_manual_schema(database_path: Path) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE students (
                id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                PRIMARY KEY (tenant_id, id)
            );
            CREATE TABLE academic_years (
                id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                PRIMARY KEY (tenant_id, id)
            );
            CREATE TABLE academic_classes (
                id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                PRIMARY KEY (tenant_id, id)
            );
            CREATE TABLE academic_options (
                id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                name TEXT NOT NULL,
                code TEXT NOT NULL,
                active INTEGER NOT NULL,
                PRIMARY KEY (tenant_id, id),
                UNIQUE (tenant_id, code)
            );
            CREATE TABLE student_assignments (
                id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                academic_year_id TEXT NOT NULL,
                academic_class_id TEXT NOT NULL,
                academic_option_id TEXT,
                status TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                closed_at TEXT,
                PRIMARY KEY (tenant_id, id),
                FOREIGN KEY (tenant_id, student_id)
                    REFERENCES students (tenant_id, id),
                FOREIGN KEY (tenant_id, academic_year_id)
                    REFERENCES academic_years (tenant_id, id),
                FOREIGN KEY (tenant_id, academic_class_id)
                    REFERENCES academic_classes (tenant_id, id),
                FOREIGN KEY (tenant_id, academic_option_id)
                    REFERENCES academic_options (tenant_id, id)
            );
            """,
        )
    connection.close()


def seed_assignment(database_path: Path, tenant_id: UUID, assignment_id: UUID) -> None:
    student_id, year_id, class_id, option_id, user_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            "INSERT INTO students (id, tenant_id) VALUES (?, ?)",
            (str(student_id), str(tenant_id)),
        )
        connection.execute(
            "INSERT INTO academic_years (id, tenant_id) VALUES (?, ?)",
            (str(year_id), str(tenant_id)),
        )
        connection.execute(
            "INSERT INTO academic_classes (id, tenant_id) VALUES (?, ?)",
            (str(class_id), str(tenant_id)),
        )
        connection.execute(
            """
            INSERT INTO academic_options (id, tenant_id, name, code, active)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(option_id), str(tenant_id), "Option test", "OPT-TEST", 1),
        )
        connection.execute(
            """
            INSERT INTO student_assignments
                (id, tenant_id, student_id, academic_year_id, academic_class_id,
                 academic_option_id, status, created_by, created_at, updated_at, closed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (str(assignment_id), str(tenant_id), str(student_id), str(year_id), str(class_id),
             str(option_id), "ACTIVE", str(user_id), now, now, None),
        )
    connection.close()


def test_repository_closes_and_reloads_assignment_without_migrations() -> None:
    with TemporaryDirectory(prefix="edunova-assignment-") as directory:
        database_path = Path(directory) / "isolated.db"
        create_manual_schema(database_path)
        assignment_id = uuid4()
        seed_assignment(database_path, TENANT_ID, assignment_id)
        repository = SQLiteStudentAssignmentRepository(ClosingSQLiteDatabase(database_path))

        current = repository.find_by_id(assignment_id, TENANT_ID)
        assert current is not None
        closed = current.close()
        repository.update(closed, StudentAssignmentStatus.ACTIVE.value)

        reloaded = repository.find_by_id(assignment_id, TENANT_ID)
        assert reloaded is not None
        assert reloaded.status is StudentAssignmentStatus.CLOSED
        assert reloaded.closed_at is not None


def test_repository_is_tenant_scoped_and_rejects_second_close() -> None:
    with TemporaryDirectory(prefix="edunova-assignment-") as directory:
        database_path = Path(directory) / "isolated.db"
        create_manual_schema(database_path)
        assignment_id = uuid4()
        seed_assignment(database_path, TENANT_ID, assignment_id)
        repository = SQLiteStudentAssignmentRepository(ClosingSQLiteDatabase(database_path))

        assert repository.find_by_id(assignment_id, OTHER_TENANT_ID) is None
        current = repository.find_by_id(assignment_id, TENANT_ID)
        assert current is not None
        closed = current.close()
        repository.update(closed, StudentAssignmentStatus.ACTIVE.value)

        with pytest.raises(ValueError, match="deja ete modifiee"):
            repository.update(closed, StudentAssignmentStatus.ACTIVE.value)

        assert repository.find_by_id(assignment_id, OTHER_TENANT_ID) is None
