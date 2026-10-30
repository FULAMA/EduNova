import sqlite3
import threading
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus
from src.academic.domain.entities.student_assignment import StudentAssignment, StudentAssignmentStatus
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.persistence.migrations.versions.migration_020_school_years_assignments import upgrade as upgrade_020
from src.infrastructure.repositories.sqlite_academic_year_repository import SQLiteAcademicYearRepository
from src.infrastructure.repositories.sqlite_student_assignment_repository import SQLiteStudentAssignmentRepository


def create_isolated_sqlite_db(db_path: Path) -> SQLiteDatabase:
    """
    Creates an isolated SQLiteDatabase on a specific temporary file,
    and creates the exact schema of migration 020 without running global initialize()
    or touching any existing database.
    """
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    upgrade_020(conn)
    conn.commit()
    conn.close()
    return SQLiteDatabase(db_path)


# =========================================================================
# Tests SQLiteAcademicYearRepository
# =========================================================================

def test_sqlite_academic_year_save_and_find(tmp_path: Path):
    db = create_isolated_sqlite_db(tmp_path / "test_year.db")
    repo = SQLiteAcademicYearRepository(db)
    tenant_id = uuid4()
    year_id = uuid4()

    year = AcademicYear(
        id=year_id,
        tenant_id=tenant_id,
        label="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 7, 31),
        status=AcademicYearStatus.DRAFT,
    )
    repo.save(year)

    found = repo.find_by_id(year_id, tenant_id)
    assert found is not None
    assert found.id == year_id
    assert found.tenant_id == tenant_id
    assert found.label == "2026-2027"
    assert found.status is AcademicYearStatus.DRAFT

    # Search with wrong tenant returns None (isolation)
    assert repo.find_by_id(year_id, uuid4()) is None


def test_sqlite_academic_year_update_status_and_phantom_success_prevention(tmp_path: Path):
    db = create_isolated_sqlite_db(tmp_path / "test_year_phantom.db")
    repo = SQLiteAcademicYearRepository(db)
    tenant_id = uuid4()
    year_id = uuid4()

    year = AcademicYear(
        id=year_id,
        tenant_id=tenant_id,
        label="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 7, 31),
        status=AcademicYearStatus.DRAFT,
    )
    repo.save(year)

    # Valid update
    activated = year.activate()
    repo.update_status(activated)
    updated_year = repo.find_by_id(year_id, tenant_id)
    assert updated_year is not None
    assert updated_year.status is AcademicYearStatus.ACTIVE

    # Update for non-existent year or wrong tenant raises ValueError (no phantom success)
    other_tenant_year = AcademicYear(
        id=year_id,
        tenant_id=uuid4(),
        label="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 7, 31),
        status=AcademicYearStatus.CLOSED,
    )
    with pytest.raises(ValueError, match="n'a pas pu etre mise a jour"):
        repo.update_status(other_tenant_year)


def test_sqlite_academic_year_unique_active_constraint_in_db(tmp_path: Path):
    """
    Checks that the partial unique index uq_academic_year_active
    enforces single ACTIVE year at SQLite level.
    """
    db = create_isolated_sqlite_db(tmp_path / "test_year_unique.db")
    repo = SQLiteAcademicYearRepository(db)
    tenant_id = uuid4()

    year1 = AcademicYear(
        id=uuid4(), tenant_id=tenant_id, label="2025-2026",
        start_date=date(2025, 9, 1), end_date=date(2026, 7, 31),
        status=AcademicYearStatus.ACTIVE,
    )
    year2 = AcademicYear(
        id=uuid4(), tenant_id=tenant_id, label="2026-2027",
        start_date=date(2026, 9, 1), end_date=date(2027, 7, 31),
        status=AcademicYearStatus.DRAFT,
    )
    repo.save(year1)
    repo.save(year2)

    # Attempting to activate year2 in SQLite raises IntegrityError due to uq_academic_year_active
    with pytest.raises(sqlite3.IntegrityError):
        repo.update_status(year2.activate())


def test_sqlite_academic_year_concurrent_activations(tmp_path: Path):
    """
    Two concurrent threads attempt to activate two different DRAFT years in the same tenant.
    Exactly one must succeed, and the other must fail with IntegrityError.
    """
    db_path = tmp_path / "test_year_concurrency.db"
    db = create_isolated_sqlite_db(db_path)
    repo = SQLiteAcademicYearRepository(db)
    tenant_id = uuid4()

    year1 = AcademicYear(
        id=uuid4(), tenant_id=tenant_id, label="2025-2026",
        start_date=date(2025, 9, 1), end_date=date(2026, 7, 31),
        status=AcademicYearStatus.DRAFT,
    )
    year2 = AcademicYear(
        id=uuid4(), tenant_id=tenant_id, label="2026-2027",
        start_date=date(2026, 9, 1), end_date=date(2027, 7, 31),
        status=AcademicYearStatus.DRAFT,
    )
    repo.save(year1)
    repo.save(year2)

    results = []
    errors = []
    barrier = threading.Barrier(2)

    def activate_year(year: AcademicYear):
        # Each thread gets its own independent SQLite connection
        thread_db = SQLiteDatabase(db_path)
        thread_repo = SQLiteAcademicYearRepository(thread_db)
        barrier.wait()
        try:
            thread_repo.update_status(year.activate())
            results.append(year.id)
        except Exception as e:
            errors.append(e)

    t1 = threading.Thread(target=activate_year, args=(year1,))
    t2 = threading.Thread(target=activate_year, args=(year2,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert len(results) == 1, f"Expected exactly 1 successful activation, got {len(results)}"
    assert len(errors) == 1, f"Expected exactly 1 error, got {len(errors)}"
    assert isinstance(errors[0], sqlite3.IntegrityError)

    # Verify that in database, exactly one is ACTIVE
    active_years = [y for y in repo.list_by_tenant(tenant_id) if y.status is AcademicYearStatus.ACTIVE]
    assert len(active_years) == 1


# =========================================================================
# Tests SQLiteStudentAssignmentRepository
# =========================================================================

def setup_assignment_tables_with_fks(conn: sqlite3.Connection, tenant_id: UUID, student_id: UUID, year_id: UUID, class_id: UUID):
    """Inserts mock rows for foreign keys referenced by student_assignments."""
    conn.execute("CREATE TABLE IF NOT EXISTS students (tenant_id TEXT, id TEXT, PRIMARY KEY (tenant_id, id))")
    conn.execute("CREATE TABLE IF NOT EXISTS academic_classes (tenant_id TEXT, id TEXT, PRIMARY KEY (tenant_id, id))")
    conn.execute("CREATE TABLE IF NOT EXISTS academic_options (tenant_id TEXT, id TEXT, PRIMARY KEY (tenant_id, id))")
    conn.execute("INSERT INTO students VALUES (?, ?)", (str(tenant_id), str(student_id)))
    conn.execute("INSERT INTO academic_classes VALUES (?, ?)", (str(tenant_id), str(class_id)))


def test_sqlite_assignment_save_and_conditional_update(tmp_path: Path):
    db_path = tmp_path / "test_assignment.db"
    db = create_isolated_sqlite_db(db_path)
    tenant_id, student_id, year_id, class_id = uuid4(), uuid4(), uuid4(), uuid4()

    with db.connect() as conn:
        setup_assignment_tables_with_fks(conn, tenant_id, student_id, year_id, class_id)
        conn.execute("INSERT INTO academic_years (id, tenant_id, label, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?)",
                     (str(year_id), str(tenant_id), "2026-2027", "2026-09-01", "2027-07-31", "ACTIVE"))

    repo = SQLiteStudentAssignmentRepository(db)
    now = datetime.now(timezone.utc)
    assignment = StudentAssignment(
        id=uuid4(), tenant_id=tenant_id, student_id=student_id,
        academic_year_id=year_id, academic_class_id=class_id, academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT, created_by=uuid4(),
        created_at=now, updated_at=now,
    )
    repo.save(assignment)

    found = repo.find_by_id(assignment.id, tenant_id)
    assert found is not None
    assert found.status is StudentAssignmentStatus.DRAFT

    # Valid conditional update DRAFT -> ACTIVE
    activated = assignment.activate()
    repo.update(activated, expected_status=StudentAssignmentStatus.DRAFT.value)
    updated_assignment = repo.find_by_id(assignment.id, tenant_id)
    assert updated_assignment is not None
    assert updated_assignment.status is StudentAssignmentStatus.ACTIVE

    # Attempting conditional update expecting DRAFT again must fail with ValueError
    with pytest.raises(ValueError, match="a deja ete modifiee"):
        repo.update(activated, expected_status=StudentAssignmentStatus.DRAFT.value)


def test_sqlite_assignment_concurrent_activations(tmp_path: Path):
    """
    Two concurrent threads attempt to activate two assignments for the SAME student and SAME year.
    The partial unique index uq_student_assignment_active guarantees only one ACTIVE assignment.
    """
    db_path = tmp_path / "test_assign_concurrency.db"
    db = create_isolated_sqlite_db(db_path)
    tenant_id, student_id, year_id, class_id = uuid4(), uuid4(), uuid4(), uuid4()

    with db.connect() as conn:
        setup_assignment_tables_with_fks(conn, tenant_id, student_id, year_id, class_id)
        conn.execute("INSERT INTO academic_years (id, tenant_id, label, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?)",
                     (str(year_id), str(tenant_id), "2026-2027", "2026-09-01", "2027-07-31", "ACTIVE"))

    repo = SQLiteStudentAssignmentRepository(db)
    now = datetime.now(timezone.utc)
    assign1 = StudentAssignment(
        id=uuid4(), tenant_id=tenant_id, student_id=student_id,
        academic_year_id=year_id, academic_class_id=class_id, academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT, created_by=uuid4(), created_at=now, updated_at=now,
    )
    assign2 = StudentAssignment(
        id=uuid4(), tenant_id=tenant_id, student_id=student_id,
        academic_year_id=year_id, academic_class_id=class_id, academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT, created_by=uuid4(), created_at=now, updated_at=now,
    )
    repo.save(assign1)
    repo.save(assign2)

    results = []
    errors = []
    barrier = threading.Barrier(2)

    def activate_assignment(a: StudentAssignment):
        thread_db = SQLiteDatabase(db_path)
        thread_repo = SQLiteStudentAssignmentRepository(thread_db)
        barrier.wait()
        try:
            thread_repo.update(a.activate(), expected_status=StudentAssignmentStatus.DRAFT.value)
            results.append(a.id)
        except Exception as e:
            errors.append(e)

    t1 = threading.Thread(target=activate_assignment, args=(assign1,))
    t2 = threading.Thread(target=activate_assignment, args=(assign2,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert len(results) == 1, f"Expected 1 success, got {len(results)}"
    assert len(errors) == 1, f"Expected 1 error, got {len(errors)}"
    assert isinstance(errors[0], sqlite3.IntegrityError)

    # In DB, exactly one is ACTIVE
    active_assignments = [
        a for a in repo.list_by_student(student_id, tenant_id)
        if a.status is StudentAssignmentStatus.ACTIVE
    ]
    assert len(active_assignments) == 1


# =========================================================================
# Tests End-to-End Use Cases with SQLite and Concurrency (Lot 4)
# =========================================================================

from src.academic.application.exceptions import ActiveConflictError  # noqa: E402
from src.academic.application.use_cases.change_academic_year_status import ChangeAcademicYearStatus  # noqa: E402
from src.academic.application.use_cases.change_student_assignment_status import ChangeStudentAssignmentStatus  # noqa: E402


def test_use_case_sequential_conflict_raises_active_conflict_error(tmp_path: Path):
    """
    Verifies that sequential attempt to activate a second year in same tenant
    raises ActiveConflictError at application level.
    """
    db_path = tmp_path / "test_uc_seq.db"
    db = create_isolated_sqlite_db(db_path)
    tenant_id = uuid4()
    repo = SQLiteAcademicYearRepository(db)

    year1 = AcademicYear(
        id=uuid4(), tenant_id=tenant_id, label="2025-2026",
        start_date=date(2025, 9, 1), end_date=date(2026, 7, 31),
        status=AcademicYearStatus.DRAFT,
    )
    year2 = AcademicYear(
        id=uuid4(), tenant_id=tenant_id, label="2026-2027",
        start_date=date(2026, 9, 1), end_date=date(2027, 7, 31),
        status=AcademicYearStatus.DRAFT,
    )
    repo.save(year1)
    repo.save(year2)

    use_case = ChangeAcademicYearStatus(repo)
    # 1. First year activates successfully
    use_case.activate(year1.id, tenant_id)
    assert repo.find_by_id(year1.id, tenant_id).status is AcademicYearStatus.ACTIVE

    # 2. Second year activation fails with ActiveConflictError
    with pytest.raises(ActiveConflictError, match="Une autre annee scolaire est deja active"):
        use_case.activate(year2.id, tenant_id)


def test_use_case_concurrent_activations_end_to_end(tmp_path: Path):
    """
    Tests two independent ChangeAcademicYearStatus instances executing concurrently
    on separate SQLiteDatabase connections against the same DB file.
    Exactly one succeeds; the second encounters either ActiveConflictError or sqlite3.IntegrityError.
    """
    db_path = tmp_path / "test_uc_concurrency.db"
    db = create_isolated_sqlite_db(db_path)
    tenant_id = uuid4()
    repo = SQLiteAcademicYearRepository(db)

    year1 = AcademicYear(
        id=uuid4(), tenant_id=tenant_id, label="2025-2026",
        start_date=date(2025, 9, 1), end_date=date(2026, 7, 31),
        status=AcademicYearStatus.DRAFT,
    )
    year2 = AcademicYear(
        id=uuid4(), tenant_id=tenant_id, label="2026-2027",
        start_date=date(2026, 9, 1), end_date=date(2027, 7, 31),
        status=AcademicYearStatus.DRAFT,
    )
    repo.save(year1)
    repo.save(year2)

    results = []
    errors = []
    barrier = threading.Barrier(2)

    def run_use_case(target_year_id: UUID):
        thread_db = SQLiteDatabase(db_path)
        thread_repo = SQLiteAcademicYearRepository(thread_db)
        thread_use_case = ChangeAcademicYearStatus(thread_repo)
        barrier.wait()
        try:
            thread_use_case.activate(target_year_id, tenant_id)
            results.append(target_year_id)
        except Exception as e:
            errors.append(e)

    t1 = threading.Thread(target=run_use_case, args=(year1.id,))
    t2 = threading.Thread(target=run_use_case, args=(year2.id,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert len(results) == 1, f"Expected 1 success, got {len(results)}"
    assert len(errors) == 1, f"Expected 1 error, got {len(errors)}"
    # Either caught at pre-read by ActiveConflictError or caught at write by IntegrityError
    assert isinstance(errors[0], (ActiveConflictError, sqlite3.IntegrityError))

    # In database, exactly one is ACTIVE
    active_years = [y for y in repo.list_by_tenant(tenant_id) if y.status is AcademicYearStatus.ACTIVE]
    assert len(active_years) == 1


def test_use_case_assignment_concurrent_activations_end_to_end(tmp_path: Path):
    """
    Tests two independent ChangeStudentAssignmentStatus instances executing concurrently
    on separate SQLiteDatabase connections against the same DB file for the same student and year.
    """
    db_path = tmp_path / "test_uc_assign_concurrency.db"
    db = create_isolated_sqlite_db(db_path)
    tenant_id, student_id, year_id, class_id = uuid4(), uuid4(), uuid4(), uuid4()

    with db.connect() as conn:
        setup_assignment_tables_with_fks(conn, tenant_id, student_id, year_id, class_id)
        conn.execute("INSERT INTO academic_years (id, tenant_id, label, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?)",
                     (str(year_id), str(tenant_id), "2026-2027", "2026-09-01", "2027-07-31", "ACTIVE"))

    repo = SQLiteStudentAssignmentRepository(db)
    now = datetime.now(timezone.utc)
    assign1 = StudentAssignment(
        id=uuid4(), tenant_id=tenant_id, student_id=student_id,
        academic_year_id=year_id, academic_class_id=class_id, academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT, created_by=uuid4(), created_at=now, updated_at=now,
    )
    assign2 = StudentAssignment(
        id=uuid4(), tenant_id=tenant_id, student_id=student_id,
        academic_year_id=year_id, academic_class_id=class_id, academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT, created_by=uuid4(), created_at=now, updated_at=now,
    )
    repo.save(assign1)
    repo.save(assign2)

    results = []
    errors = []
    barrier = threading.Barrier(2)

    def run_assignment_use_case(target_assignment_id: UUID):
        thread_db = SQLiteDatabase(db_path)
        thread_assign_repo = SQLiteStudentAssignmentRepository(thread_db)
        thread_year_repo = SQLiteAcademicYearRepository(thread_db)
        thread_use_case = ChangeStudentAssignmentStatus(thread_assign_repo, thread_year_repo)
        barrier.wait()
        try:
            thread_use_case.activate(target_assignment_id, tenant_id)
            results.append(target_assignment_id)
        except Exception as e:
            errors.append(e)

    t1 = threading.Thread(target=run_assignment_use_case, args=(assign1.id,))
    t2 = threading.Thread(target=run_assignment_use_case, args=(assign2.id,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert len(results) == 1, f"Expected 1 success, got {len(results)}"
    assert len(errors) == 1, f"Expected 1 error, got {len(errors)}"
    assert isinstance(errors[0], (ActiveConflictError, sqlite3.IntegrityError))

    active_assignments = [
        a for a in repo.list_by_student(student_id, tenant_id)
        if a.status is StudentAssignmentStatus.ACTIVE
    ]
    assert len(active_assignments) == 1


# =========================================================================
# Tests HTTP 409 Translation on Isolated FastAPI TestClient
# =========================================================================

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from src.presentation.api.routes.academic_years import router as academic_years_router  # noqa: E402
from src.presentation.api.routes.student_assignments import router as student_assignments_router  # noqa: E402
from src.presentation.api.dependencies import (  # noqa: E402
    get_change_academic_year_status_use_case,
    get_change_student_assignment_status_use_case,
)
from src.presentation.api.dependencies.auth import get_tenant_context, get_current_user  # noqa: E402
from src.shared.application.context.tenant_context import TenantContext  # noqa: E402
from src.identity.application.dto.authenticated_user import AuthenticatedUser  # noqa: E402


def test_http_409_translation_for_both_errors(tmp_path: Path):
    """
    Confirms that both ActiveConflictError (application-level) and sqlite3.IntegrityError
    are uniformly translated to HTTP 409 Conflict by the FastAPI routes.
    """
    db_path = tmp_path / "test_http_isolated.db"
    db = create_isolated_sqlite_db(db_path)
    tenant_id = uuid4()
    user_id = uuid4()

    year_repo = SQLiteAcademicYearRepository(db)
    assign_repo = SQLiteStudentAssignmentRepository(db)

    year_use_case = ChangeAcademicYearStatus(year_repo)
    assign_use_case = ChangeStudentAssignmentStatus(assign_repo, year_repo)

    app = FastAPI()
    app.include_router(academic_years_router)
    app.include_router(student_assignments_router)

    from src.presentation.api.dependencies import get_membership_repository
    from unittest.mock import MagicMock

    mock_membership_repo = MagicMock()
    mock_membership = MagicMock()
    mock_membership.active = True
    mock_membership.role = "ADMIN"
    mock_membership_repo.find_by_user_and_tenant.return_value = mock_membership

    app.dependency_overrides[get_change_academic_year_status_use_case] = lambda: year_use_case
    app.dependency_overrides[get_change_student_assignment_status_use_case] = lambda: assign_use_case
    app.dependency_overrides[get_tenant_context] = lambda: TenantContext(tenant_id)
    app.dependency_overrides[get_membership_repository] = lambda: mock_membership_repo
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(user_id, "admin@test.com", "ADMIN", True, True)

    client = TestClient(app)

    # 1. Test AcademicYear HTTP 409 on second activation
    year1 = AcademicYear(id=uuid4(), tenant_id=tenant_id, label="2025-2026", start_date=date(2025, 9, 1), end_date=date(2026, 7, 31), status=AcademicYearStatus.DRAFT)
    year2 = AcademicYear(id=uuid4(), tenant_id=tenant_id, label="2026-2027", start_date=date(2026, 9, 1), end_date=date(2027, 7, 31), status=AcademicYearStatus.DRAFT)
    year_repo.save(year1)
    year_repo.save(year2)

    res1 = client.post(f"/academic-years/{year1.id}/activate")
    assert res1.status_code == 200

    # Sequential activation of year2 hits ActiveConflictError -> HTTP 409
    res2 = client.post(f"/academic-years/{year2.id}/activate")
    assert res2.status_code == 409
    assert "Une autre annee" in res2.json()["detail"]

    # Other error (e.g., non-existent year) returns HTTP 400
    res_bad = client.post(f"/academic-years/{uuid4()}/activate")
    assert res_bad.status_code == 400

    # 2. Test StudentAssignment HTTP 409 on second activation
    student_id = uuid4()
    class_id = uuid4()
    with db.connect() as conn:
        setup_assignment_tables_with_fks(conn, tenant_id, student_id, year1.id, class_id)

    now = datetime.now(timezone.utc)
    assign1 = StudentAssignment(
        id=uuid4(), tenant_id=tenant_id, student_id=student_id,
        academic_year_id=year1.id, academic_class_id=class_id, academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT, created_by=user_id, created_at=now, updated_at=now,
    )
    assign2 = StudentAssignment(
        id=uuid4(), tenant_id=tenant_id, student_id=student_id,
        academic_year_id=year1.id, academic_class_id=class_id, academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT, created_by=user_id, created_at=now, updated_at=now,
    )
    assign_repo.save(assign1)
    assign_repo.save(assign2)

    res_a1 = client.post(f"/student-assignments/{assign1.id}/activate")
    assert res_a1.status_code == 200

    # Sequential activation of assign2 hits ActiveConflictError -> HTTP 409
    res_a2 = client.post(f"/student-assignments/{assign2.id}/activate")
    assert res_a2.status_code == 409
    assert "Une affectation active existe deja" in res_a2.json()["detail"]

    # Other error (e.g., non-existent assignment) returns HTTP 400
    res_a_bad = client.post(f"/student-assignments/{uuid4()}/activate")
    assert res_a_bad.status_code == 400

    # 3. Test that non-unique IntegrityErrors (e.g., Foreign Key or other DB error) are NOT reported as 409 active conflict
    class FailingForeignKeyUseCase:
        def activate(self, year_id, tenant_id):
            raise sqlite3.IntegrityError("FOREIGN KEY constraint failed")

    app.dependency_overrides[get_change_academic_year_status_use_case] = lambda: FailingForeignKeyUseCase()
    res_fk = client.post(f"/academic-years/{year1.id}/activate")
    assert res_fk.status_code == 400
    assert "Erreur d'integrite" in res_fk.json()["detail"]
    assert "Une autre annee" not in res_fk.json()["detail"]

    class FailingForeignKeyAssignmentUseCase:
        def activate(self, assignment_id, tenant_id):
            raise sqlite3.IntegrityError("FOREIGN KEY constraint failed")

    app.dependency_overrides[get_change_student_assignment_status_use_case] = lambda: FailingForeignKeyAssignmentUseCase()
    res_a_fk = client.post(f"/student-assignments/{assign1.id}/activate")
    assert res_a_fk.status_code == 400
    assert "Erreur d'integrite" in res_a_fk.json()["detail"]
    assert "Une affectation active" not in res_a_fk.json()["detail"]

    # 4. Verify cross-tenant isolation: activating a year from another tenant via use case raises ValueError
    other_tenant_id = uuid4()
    app.dependency_overrides[get_change_academic_year_status_use_case] = lambda: year_use_case
    app.dependency_overrides[get_change_student_assignment_status_use_case] = lambda: assign_use_case
    app.dependency_overrides[get_tenant_context] = lambda: TenantContext(other_tenant_id)

    res_cross_year = client.post(f"/academic-years/{year1.id}/activate")
    assert res_cross_year.status_code == 400
    assert "introuvable" in res_cross_year.json()["detail"]

    res_cross_assign = client.post(f"/student-assignments/{assign1.id}/activate")
    assert res_cross_assign.status_code == 400
    assert "introuvable" in res_cross_assign.json()["detail"]

    # Verify final state in DB has not changed
    found_year1 = year_repo.find_by_id(year1.id, tenant_id)
    assert found_year1 is not None and found_year1.status is AcademicYearStatus.ACTIVE
    found_year2 = year_repo.find_by_id(year2.id, tenant_id)
    assert found_year2 is not None and found_year2.status is AcademicYearStatus.DRAFT


