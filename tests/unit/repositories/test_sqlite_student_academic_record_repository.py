import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from uuid import uuid4

from src.academic.domain.entities.student_academic_record import (
    AcademicRecordStatus,
    StudentAcademicRecord,
)
from src.academic.domain.value_objects.subject_result import SubjectResult
from src.academic.application.dto.add_subject_result_request import AddSubjectResultRequest
from src.academic.application.exceptions import AcademicRecordConcurrencyError
from src.academic.application.use_cases.add_subject_result import AddSubjectResult
from src.infrastructure.repositories.sqlite_student_academic_record_repository import (
    SQLiteStudentAcademicRecordRepository,
)
from src.infrastructure.persistence.database import SQLiteDatabase
from tests.support.academic_eligibility import eligible_result_repositories


def create_test_database(tmp_path):
    database_path = tmp_path / "test.db"

    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")

    connection.executescript("""
        CREATE TABLE students (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            active INTEGER NOT NULL
        );

        CREATE UNIQUE INDEX uq_students_tenant_id
        ON students (tenant_id, id);

        CREATE TABLE student_academic_records (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            general_average REAL NOT NULL,
            failed_subjects INTEGER NOT NULL,
            credits_obtained REAL NOT NULL,
            total_credits REAL NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'DRAFT',

            PRIMARY KEY (student_id, academic_period_id),

            FOREIGN KEY (tenant_id, student_id)
            REFERENCES students (tenant_id, id)
        );

        CREATE UNIQUE INDEX
        uq_student_academic_records_tenant_student_period
        ON student_academic_records (
            tenant_id,
            student_id,
            academic_period_id
        );

        CREATE TABLE subject_results (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            average REAL NOT NULL,
            coefficient REAL NOT NULL,
            position INTEGER NOT NULL,

            FOREIGN KEY (
                tenant_id,
                student_id,
                academic_period_id
            )
            REFERENCES student_academic_records (
                tenant_id,
                student_id,
                academic_period_id
            )
        );
    """)

    connection.commit()
    connection.close()

    return SQLiteDatabase(str(database_path))


def make_record(tenant_id, student_id, period_id):
    return StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=15.0,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )


def insert_student(database, student_id, tenant_id):
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO students (
                id,
                tenant_id,
                first_name,
                last_name,
                active
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(student_id),
                str(tenant_id),
                "Jean",
                "Test",
                1,
            ),
        )


def insert_record(database, record, tenant_id):
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO student_academic_records (
                student_id,
                academic_period_id,
                tenant_id,
                general_average,
                failed_subjects,
                credits_obtained,
                total_credits
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(record.student_id),
                str(record.academic_period_id),
                str(tenant_id),
                record.general_average,
                record.failed_subjects,
                record.credits_obtained,
                record.total_credits,
            ),
        )


def test_find_by_student_and_period_requires_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()

    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_a)

    record = make_record(tenant_a, student_id, period_id)
    insert_record(database, record, tenant_a)

    result = repository.find_by_student_and_period(
        student_id,
        period_id,
        tenant_a,
    )

    assert result is not None
    assert result.student_id == student_id
    assert result.tenant_id == tenant_a


def test_find_by_student_and_period_cannot_cross_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_a)

    record = make_record(tenant_a, student_id, period_id)
    insert_record(database, record, tenant_a)

    result = repository.find_by_student_and_period(
        student_id,
        period_id,
        tenant_b,
    )

    assert result is None

def test_find_by_student_requires_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()

    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_a)

    record = make_record(tenant_a, student_id, period_id)
    insert_record(database, record, tenant_a)

    result = repository.find_by_student(
        student_id,
        tenant_a,
    )

    assert result is not None
    assert result.student_id == student_id
    assert result.tenant_id == tenant_a


def test_find_by_student_cannot_cross_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_a)

    record = make_record(tenant_a, student_id, period_id)
    insert_record(database, record, tenant_a)

    result = repository.find_by_student(
        student_id,
        tenant_b,
    )

    assert result is None

def test_save_persists_tenant_id(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_id = uuid4()
    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_id)

    record = make_record(
        tenant_id,
        student_id,
        period_id,
    )

    repository.save(record)

    with database.connect() as connection:
        row = connection.execute(
            """
            SELECT
                tenant_id,
                student_id,
                academic_period_id
            FROM student_academic_records
            WHERE student_id = ?
              AND academic_period_id = ?
              AND tenant_id = ?
            """,
            (
                str(student_id),
                str(period_id),
                str(tenant_id),
            ),
        ).fetchone()

    assert row is not None
    assert row["tenant_id"] == str(tenant_id)
    assert row["student_id"] == str(student_id)
    assert row["academic_period_id"] == str(period_id)


def test_save_cannot_assign_record_to_another_tenant_student(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_a)

    record = make_record(
        tenant_b,
        student_id,
        period_id,
    )

    with pytest.raises(sqlite3.IntegrityError):
        repository.save(record)


def test_save_persists_subject_results_for_same_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_id = uuid4()
    student_id = uuid4()
    period_id = uuid4()
    subject_id = uuid4()

    insert_student(database, student_id, tenant_id)

    record = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(
            SubjectResult(
                subject_id=subject_id,
                average=15.0,
                coefficient=2.0,
            ),
        ),
        general_average=15.0,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )

    repository.save(record)

    with database.connect() as connection:
        row = connection.execute(
            """
            SELECT
                student_id,
                academic_period_id,
                subject_id
            FROM subject_results
            WHERE student_id = ?
              AND academic_period_id = ?
              AND subject_id = ?
            """,
            (
                str(student_id),
                str(period_id),
                str(subject_id),
            ),
        ).fetchone()

    assert row is not None
    assert row["student_id"] == str(student_id)
    assert row["academic_period_id"] == str(period_id)
    assert row["subject_id"] == str(subject_id)


def test_find_by_student_and_period_does_not_read_subject_results_from_another_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    student_a = uuid4()
    student_b = uuid4()
    period_id = uuid4()

    subject_a = uuid4()
    subject_b = uuid4()

    insert_student(database, student_a, tenant_a)
    insert_student(database, student_b, tenant_b)

    insert_record(
        database,
        make_record(
            tenant_b,
            student_b,
            period_id,
        ),
        tenant_b,
    )

    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO student_academic_records (
                student_id,
                academic_period_id,
                tenant_id,
                general_average,
                failed_subjects,
                credits_obtained,
                total_credits
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(student_a),
                str(period_id),
                str(tenant_a),
                15.0,
                0,
                30.0,
                30.0,
            ),
        )

        connection.execute(
            """
            INSERT INTO subject_results (
                student_id,
                academic_period_id,
                tenant_id,
                subject_id,
                average,
                coefficient,
                position
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(student_a),
                str(period_id),
                str(tenant_a),
                str(subject_a),
                15.0,
                2.0,
                0,
            ),
        )

        connection.execute(
            """
            INSERT INTO subject_results (
                student_id,
                academic_period_id,
                tenant_id,
                subject_id,
                average,
                coefficient,
                position
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(student_b),
                str(period_id),
                str(tenant_b),
                str(subject_b),
                18.0,
                3.0,
                0,
            ),
        )

    result = repository.find_by_student_and_period(
        student_a,
        period_id,
        tenant_a,
    )

    assert result is not None
    assert len(result.subject_results) == 1
    assert result.subject_results[0].subject_id == subject_a









def test_save_and_find_preserves_version(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_id = uuid4()
    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_id)

    record = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=15.0,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
        version=2,
    )

    repository.save(record)

    result = repository.find_by_student_and_period(
        student_id,
        period_id,
        tenant_id,
    )

    assert result is not None
    assert result.version == 2






def test_save_and_find_preserves_draft_status(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_id = uuid4()
    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_id)

    record = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=15.0,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
        status=AcademicRecordStatus.DRAFT,
    )

    repository.save(record)

    result = repository.find_by_student_and_period(
        student_id,
        period_id,
        tenant_id,
    )

    assert result is not None
    assert result.status == AcademicRecordStatus.DRAFT


def test_save_and_find_preserves_validated_status(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_id = uuid4()
    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_id)

    draft = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=15.0,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )

    validated = draft.validate()

    repository.save(validated)

    result = repository.find_by_student_and_period(
        student_id,
        period_id,
        tenant_id,
    )

    assert result is not None
    assert result.status == AcademicRecordStatus.VALIDATED

    with pytest.raises(ValueError):
        result.with_subject_result(
            SubjectResult(
                subject_id=uuid4(),
                average=15.0,
                coefficient=1.0,
            )
        )

    corrected = result.create_new_version(
        general_average=16.0,
        failed_subjects=0,
        credits_obtained=30.0,
    )

    assert corrected.status == AcademicRecordStatus.VALIDATED
    assert corrected.version == result.version + 1


def test_save_updates_existing_subject_results_without_replacing_parent(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_id = uuid4()
    student_id = uuid4()
    period_id = uuid4()

    subject_a = uuid4()
    subject_b = uuid4()
    subject_c = uuid4()

    insert_student(database, student_id, tenant_id)

    first_record = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(
            SubjectResult(
                subject_id=subject_a,
                average=12.0,
                coefficient=2.0,
            ),
            SubjectResult(
                subject_id=subject_b,
                average=14.0,
                coefficient=3.0,
            ),
        ),
        general_average=13.0,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )

    repository.save(first_record)

    second_record = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(
            SubjectResult(
                subject_id=subject_c,
                average=17.0,
                coefficient=4.0,
            ),
        ),
        general_average=17.0,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
        version=2,
    )

    repository.save(second_record, expected_version=first_record.version)

    result = repository.find_by_student_and_period(
        student_id,
        period_id,
        tenant_id,
    )

    assert result is not None
    assert result.general_average == 17.0
    assert len(result.subject_results) == 1
    assert result.subject_results[0].subject_id == subject_c

    with database.connect() as connection:
        rows = connection.execute(
            """
            SELECT subject_id
            FROM subject_results
            WHERE student_id = ?
              AND academic_period_id = ?
              AND tenant_id = ?
            ORDER BY position
            """,
            (
                str(student_id),
                str(period_id),
                str(tenant_id),
            ),
        ).fetchall()

    assert len(rows) == 1
    assert rows[0]["subject_id"] == str(subject_c)


def test_concurrent_duplicate_record_insert_is_refused(tmp_path):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)
    tenant_id, student_id, period_id = uuid4(), uuid4(), uuid4()
    insert_student(database, student_id, tenant_id)
    record = make_record(tenant_id, student_id, period_id)
    barrier = Barrier(2)

    def insert():
        barrier.wait()
        try:
            repository.save(record)
            return "created"
        except ValueError as exc:
            assert str(exc) == "Academic record already exists"
            return "duplicate"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: insert(), range(2)))

    assert sorted(outcomes) == ["created", "duplicate"]
    assert repository.find_by_student_and_period(student_id, period_id, tenant_id) == record


def test_valid_finite_numeric_values_round_trip_through_sqlite(tmp_path):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)
    tenant_id, student_id, period_id, subject_id = uuid4(), uuid4(), uuid4(), uuid4()
    insert_student(database, student_id, tenant_id)
    record = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(SubjectResult(subject_id, 15.0, 1e300),),
        general_average=15.0,
        failed_subjects=0,
        credits_obtained=0.0,
        total_credits=30.0,
    )

    repository.save(record)

    loaded = repository.find_by_student_and_period(student_id, period_id, tenant_id)
    assert loaded == record


@pytest.mark.parametrize("same_subject", [False, True])
def test_concurrent_subject_additions_detect_stale_version_without_losing_result(
    tmp_path, same_subject
):
    database = create_test_database(tmp_path)
    base_repository = SQLiteStudentAcademicRecordRepository(database)
    tenant_id, student_id, period_id = uuid4(), uuid4(), uuid4()
    insert_student(database, student_id, tenant_id)
    initial = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=0.0,
        failed_subjects=0,
        credits_obtained=0.0,
        total_credits=30.0,
    )
    base_repository.save(initial)
    read_barrier = Barrier(2)

    class ConcurrentReadRepository:
        def __init__(self):
            self._read_count = 0

        def find_by_student_and_period(self, *args):
            record = base_repository.find_by_student_and_period(*args)
            self._read_count += 1
            if self._read_count <= 2:
                read_barrier.wait()
            return record

        def save(self, record, *, expected_version=None, operation="SAVE"):
            return base_repository.save(
                record, expected_version=expected_version, operation=operation
            )

    subject_ids = [uuid4(), uuid4()]
    if same_subject:
        subject_ids[1] = subject_ids[0]
    use_case = AddSubjectResult(
        ConcurrentReadRepository(), **eligible_result_repositories(subject_ids)
    )

    def add(subject_id):
        try:
            use_case.execute(AddSubjectResultRequest(
                tenant_id=tenant_id,
                student_id=student_id,
                academic_period_id=period_id,
                subject_id=subject_id,
                average=15.0,
                coefficient=2.0,
            ))
            return "added"
        except AcademicRecordConcurrencyError:
            return "stale"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(add, subject_ids))

    persisted = base_repository.find_by_student_and_period(student_id, period_id, tenant_id)
    assert sorted(outcomes) == ["added", "stale"]
    assert persisted is not None
    assert len(persisted.subject_results) == 1
    assert persisted.subject_results[0].subject_id in subject_ids
    assert persisted.version == 2
