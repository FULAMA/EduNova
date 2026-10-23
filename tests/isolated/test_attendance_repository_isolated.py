import sqlite3
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID, uuid4

import pytest

from src.academic.domain.entities.attendance import Attendance, AttendanceStatus
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_attendance_repository import SQLiteAttendanceRepository


TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
OTHER_TENANT_ID = UUID("00000000-0000-0000-0000-000000000009")


class ClosingSQLiteDatabase(SQLiteDatabase):
    def connect(self):
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

        class Context:
            def __enter__(self):
                return connection.__enter__()

            def __exit__(self, exc_type, exc_value, traceback):
                try:
                    return connection.__exit__(exc_type, exc_value, traceback)
                finally:
                    connection.close()

        return Context()


def create_schema(path: Path) -> None:
    connection = sqlite3.connect(path)
    with connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE students (id TEXT NOT NULL, tenant_id TEXT NOT NULL,
                PRIMARY KEY (tenant_id, id));
            CREATE TABLE academic_classes (id TEXT NOT NULL, tenant_id TEXT NOT NULL,
                PRIMARY KEY (tenant_id, id));
            CREATE TABLE academic_years (id TEXT NOT NULL, tenant_id TEXT NOT NULL,
                PRIMARY KEY (tenant_id, id));
            CREATE TABLE academic_periods (id TEXT NOT NULL, tenant_id TEXT NOT NULL,
                PRIMARY KEY (tenant_id, id));
            CREATE TABLE student_assignments (
                id TEXT NOT NULL, tenant_id TEXT NOT NULL, student_id TEXT NOT NULL,
                academic_year_id TEXT NOT NULL, academic_class_id TEXT NOT NULL,
                status TEXT NOT NULL, PRIMARY KEY (tenant_id, id));
            CREATE TABLE attendance_records (
                id TEXT NOT NULL, tenant_id TEXT NOT NULL, student_id TEXT NOT NULL,
                academic_class_id TEXT NOT NULL, academic_year_id TEXT NOT NULL,
                academic_period_id TEXT NOT NULL, attendance_date TEXT NOT NULL,
                status TEXT NOT NULL, justified INTEGER NOT NULL, recorded_by TEXT,
                version INTEGER NOT NULL DEFAULT 1, PRIMARY KEY (tenant_id, id),
                UNIQUE (tenant_id, student_id, attendance_date),
                FOREIGN KEY (tenant_id, student_id) REFERENCES students (tenant_id, id),
                FOREIGN KEY (tenant_id, academic_class_id) REFERENCES academic_classes (tenant_id, id),
                FOREIGN KEY (tenant_id, academic_year_id) REFERENCES academic_years (tenant_id, id),
                FOREIGN KEY (tenant_id, academic_period_id) REFERENCES academic_periods (tenant_id, id));
            CREATE TABLE attendance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL,
                attendance_id TEXT NOT NULL, version INTEGER NOT NULL,
                previous_status TEXT, previous_justified INTEGER,
                new_status TEXT NOT NULL, new_justified INTEGER NOT NULL,
                changed_by TEXT NOT NULL, changed_at TEXT NOT NULL);
            """,
        )
    connection.close()


def seed_assignment(path: Path, tenant_id: UUID) -> tuple[UUID, UUID, UUID, UUID, UUID, UUID]:
    student_id, class_id, year_id, period_id, assignment_id, actor_id = (uuid4() for _ in range(6))
    connection = sqlite3.connect(path)
    with connection:
        connection.executemany(
            "INSERT INTO students (id, tenant_id) VALUES (?, ?)", [(str(student_id), str(tenant_id))],
        )
        connection.execute("INSERT INTO academic_classes (id, tenant_id) VALUES (?, ?)", (str(class_id), str(tenant_id)))
        connection.execute("INSERT INTO academic_years (id, tenant_id) VALUES (?, ?)", (str(year_id), str(tenant_id)))
        connection.execute("INSERT INTO academic_periods (id, tenant_id) VALUES (?, ?)", (str(period_id), str(tenant_id)))
        connection.execute(
            "INSERT INTO student_assignments (id, tenant_id, student_id, academic_year_id, academic_class_id, status) VALUES (?, ?, ?, ?, ?, 'ACTIVE')",
            (str(assignment_id), str(tenant_id), str(student_id), str(year_id), str(class_id)),
        )
    connection.close()
    return student_id, class_id, year_id, period_id, assignment_id, actor_id


def test_repository_persists_recorded_by_and_isolates_tenant() -> None:
    with TemporaryDirectory(prefix="edunova-attendance-") as directory:
        path = Path(directory) / "attendance.db"
        create_schema(path)
        student_id, class_id, year_id, period_id, _, actor_id = seed_assignment(path, TENANT_ID)
        repository = SQLiteAttendanceRepository(ClosingSQLiteDatabase(path))
        attendance = Attendance(
            uuid4(), TENANT_ID, student_id, class_id, year_id, period_id,
            date(2026, 10, 19), AttendanceStatus.PRESENT, recorded_by=actor_id,
        )

        repository.record(attendance)

        loaded = repository.list_by_student_period(TENANT_ID, student_id, period_id)
        assert loaded[0].recorded_by == actor_id
        assert repository.list_by_student_period(OTHER_TENANT_ID, student_id, period_id) == ()


def test_repository_rejects_duplicate_student_day() -> None:
    with TemporaryDirectory(prefix="edunova-attendance-") as directory:
        path = Path(directory) / "attendance.db"
        create_schema(path)
        student_id, class_id, year_id, period_id, _, actor_id = seed_assignment(path, TENANT_ID)
        repository = SQLiteAttendanceRepository(ClosingSQLiteDatabase(path))
        attendance = Attendance(
            uuid4(), TENANT_ID, student_id, class_id, year_id, period_id,
            date(2026, 10, 19), AttendanceStatus.ABSENT, recorded_by=actor_id,
        )
        repository.record(attendance)

        with pytest.raises(sqlite3.IntegrityError):
            repository.record(Attendance(
                uuid4(), TENANT_ID, student_id, class_id, year_id, period_id,
                date(2026, 10, 19), AttendanceStatus.LATE, recorded_by=actor_id,
            ))


def test_repository_correction_is_versioned_and_keeps_original_author() -> None:
    with TemporaryDirectory(prefix="edunova-attendance-") as directory:
        path = Path(directory) / "attendance.db"
        create_schema(path)
        student_id, class_id, year_id, period_id, _, actor_id = seed_assignment(path, TENANT_ID)
        correction_actor = uuid4()
        repository = SQLiteAttendanceRepository(ClosingSQLiteDatabase(path))
        attendance = Attendance(
            uuid4(), TENANT_ID, student_id, class_id, year_id, period_id,
            date(2026, 10, 19), AttendanceStatus.ABSENT, recorded_by=actor_id,
        )
        repository.record(attendance)

        corrected = attendance.corrected(AttendanceStatus.PRESENT, False)
        saved = repository.correct(corrected, expected_version=1, changed_by=correction_actor)

        assert saved.version == 2
        assert saved.recorded_by == actor_id
        assert repository.find_by_id(TENANT_ID, attendance.id).status is AttendanceStatus.PRESENT
        connection = sqlite3.connect(path)
        try:
            history = connection.execute(
                    "SELECT changed_by FROM attendance_history WHERE attendance_id=? ORDER BY version",
                    (str(attendance.id),),
                ).fetchall()
        finally:
            connection.close()
        assert history[-1][0] == str(correction_actor)

        with pytest.raises(ValueError, match="modifi"):
            repository.correct(corrected, expected_version=1, changed_by=correction_actor)
