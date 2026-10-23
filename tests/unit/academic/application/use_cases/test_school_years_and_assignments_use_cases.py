from datetime import date, datetime, timezone
from uuid import UUID, uuid4

import pytest

from src.academic.application.exceptions import ActiveConflictError
from src.academic.application.interfaces.academic_class_repository import AcademicClassRepository
from src.academic.application.interfaces.academic_option_repository import AcademicOptionRepository
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.application.interfaces.class_option_repository import ClassOptionRepository
from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.application.interfaces.student_repository import StudentRepository
from src.academic.application.use_cases.change_academic_year_status import ChangeAcademicYearStatus
from src.academic.application.use_cases.change_student_assignment_status import ChangeStudentAssignmentStatus
from src.academic.application.use_cases.create_academic_year import CreateAcademicYear
from src.academic.application.use_cases.create_student_assignment import CreateStudentAssignment
from src.academic.domain.entities.academic_class import AcademicClass
from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus
from src.academic.domain.entities.student_assignment import StudentAssignment, StudentAssignmentStatus


class FakeAcademicYearRepository(AcademicYearRepository):
    def __init__(self) -> None:
        self.years: dict[UUID, AcademicYear] = {}

    def save(self, year: AcademicYear) -> None:
        self.years[year.id] = year

    def find_by_id(self, year_id: UUID, tenant_id: UUID) -> AcademicYear | None:
        year = self.years.get(year_id)
        if year and year.tenant_id == tenant_id:
            return year
        return None

    def list_by_tenant(self, tenant_id: UUID) -> tuple[AcademicYear, ...]:
        return tuple(y for y in self.years.values() if y.tenant_id == tenant_id)

    def update_status(self, year: AcademicYear) -> AcademicYear:
        self.years[year.id] = year
        return year


class FakeStudentAssignmentRepository(StudentAssignmentRepository):
    def __init__(self) -> None:
        self.assignments: dict[UUID, StudentAssignment] = {}

    def save(self, assignment: StudentAssignment) -> None:
        self.assignments[assignment.id] = assignment

    def find_by_id(self, assignment_id: UUID, tenant_id: UUID) -> StudentAssignment | None:
        a = self.assignments.get(assignment_id)
        if a and a.tenant_id == tenant_id:
            return a
        return None

    def list_by_student(self, student_id: UUID, tenant_id: UUID) -> tuple[StudentAssignment, ...]:
        return tuple(
            a for a in self.assignments.values()
            if a.student_id == student_id and a.tenant_id == tenant_id
        )

    def update(self, assignment: StudentAssignment, expected_status: str) -> StudentAssignment:
        existing = self.assignments.get(assignment.id)
        if not existing or existing.status.value != expected_status:
            raise ValueError("L'affectation a deja ete modifiee ou n'existe pas.")
        self.assignments[assignment.id] = assignment
        return assignment


class FakeStudentRepository(StudentRepository):
    def __init__(self, valid_students: set[tuple[UUID, UUID]]) -> None:
        self.valid_students = valid_students

    def get_by_id_and_tenant(self, student_id: UUID, tenant_id: UUID):
        if (student_id, tenant_id) in self.valid_students:
            return object()
        return None

    def list_by_tenant(self, tenant_id: UUID):
        return ()


class FakeAcademicClassRepository(AcademicClassRepository):
    def __init__(self, valid_classes: set[tuple[UUID, UUID]]) -> None:
        self.valid_classes = valid_classes

    def find_by_id(self, class_id: UUID, tenant_id: UUID) -> AcademicClass | None:
        if (class_id, tenant_id) in self.valid_classes:
            return AcademicClass(class_id, tenant_id, "Class 1")
        return None

    def save(self, academic_class: AcademicClass) -> None:
        pass

    def list_by_tenant(self, tenant_id: UUID):
        return ()


class FakeAcademicOptionRepository(AcademicOptionRepository):
    def __init__(self, valid_options: set[tuple[UUID, UUID]]) -> None:
        self.valid_options = valid_options

    def find_by_id(self, option_id: UUID, tenant_id: UUID):
        if (option_id, tenant_id) in self.valid_options:
            return object()
        return None

    def save(self, option) -> None:
        pass

    def list_by_tenant(self, tenant_id: UUID):
        return ()


class FakeClassOptionRepository(ClassOptionRepository):
    def __init__(self, valid_links: set[tuple[UUID, UUID, UUID]]) -> None:
        self.valid_links = valid_links

    def find_by_id(self, class_option_id: UUID, tenant_id: UUID):
        return None

    def find_by_class_and_option(self, class_id: UUID, option_id: UUID, tenant_id: UUID):
        if (class_id, option_id, tenant_id) in self.valid_links:
            return object()
        return None

    def save(self, class_option) -> None:
        pass


# =========================================================================
# Tests CreateAcademicYear
# =========================================================================

def test_create_academic_year_valid():
    repo = FakeAcademicYearRepository()
    use_case = CreateAcademicYear(repo)
    tenant_id = uuid4()

    year = use_case.execute(
        tenant_id=tenant_id,
        label="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 7, 31),
    )

    assert year.tenant_id == tenant_id
    assert year.label == "2026-2027"
    assert year.status is AcademicYearStatus.DRAFT
    assert repo.find_by_id(year.id, tenant_id) is not None


def test_create_academic_year_invalid_dates_rejected():
    repo = FakeAcademicYearRepository()
    use_case = CreateAcademicYear(repo)
    tenant_id = uuid4()

    with pytest.raises(ValueError, match="date de fin"):
        use_case.execute(
            tenant_id=tenant_id,
            label="2026-2027",
            start_date=date(2027, 9, 1),
            end_date=date(2026, 7, 31),
        )
    assert len(repo.years) == 0


# =========================================================================
# Tests ChangeAcademicYearStatus
# =========================================================================

def test_activate_academic_year_success():
    repo = FakeAcademicYearRepository()
    tenant_id = uuid4()
    year = AcademicYear(
        id=uuid4(),
        tenant_id=tenant_id,
        label="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 7, 31),
    )
    repo.save(year)

    use_case = ChangeAcademicYearStatus(repo)
    activated = use_case.activate(year.id, tenant_id)

    assert activated.status is AcademicYearStatus.ACTIVE
    assert repo.find_by_id(year.id, tenant_id).status is AcademicYearStatus.ACTIVE


def test_activate_academic_year_prevents_multiple_active():
    repo = FakeAcademicYearRepository()
    tenant_id = uuid4()
    active_year = AcademicYear(
        id=uuid4(),
        tenant_id=tenant_id,
        label="2025-2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 7, 31),
        status=AcademicYearStatus.ACTIVE,
    )
    draft_year = AcademicYear(
        id=uuid4(),
        tenant_id=tenant_id,
        label="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 7, 31),
        status=AcademicYearStatus.DRAFT,
    )
    repo.save(active_year)
    repo.save(draft_year)

    use_case = ChangeAcademicYearStatus(repo)
    with pytest.raises(ActiveConflictError, match="Une autre annee scolaire est deja active"):
        use_case.activate(draft_year.id, tenant_id)

    assert repo.find_by_id(draft_year.id, tenant_id).status is AcademicYearStatus.DRAFT


def test_activate_non_existent_year():
    repo = FakeAcademicYearRepository()
    use_case = ChangeAcademicYearStatus(repo)

    with pytest.raises(ValueError, match="Annee scolaire introuvable"):
        use_case.activate(uuid4(), uuid4())


def test_close_academic_year_success_and_cannot_reopen():
    repo = FakeAcademicYearRepository()
    tenant_id = uuid4()
    year = AcademicYear(
        id=uuid4(),
        tenant_id=tenant_id,
        label="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 7, 31),
        status=AcademicYearStatus.ACTIVE,
    )
    repo.save(year)

    use_case = ChangeAcademicYearStatus(repo)
    closed = use_case.close(year.id, tenant_id)

    assert closed.status is AcademicYearStatus.CLOSED
    with pytest.raises(ValueError, match="Une annee cloturee ne peut pas etre rouverte"):
        use_case.activate(year.id, tenant_id)


# =========================================================================
# Tests CreateStudentAssignment
# =========================================================================

def test_create_student_assignment_valid():
    tenant_id = uuid4()
    student_id = uuid4()
    class_id = uuid4()
    year_id = uuid4()
    created_by = uuid4()

    year_repo = FakeAcademicYearRepository()
    year_repo.save(AcademicYear(year_id, tenant_id, "2026-2027", date(2026, 9, 1), date(2027, 7, 31), AcademicYearStatus.ACTIVE))

    assign_repo = FakeStudentAssignmentRepository()
    student_repo = FakeStudentRepository({(student_id, tenant_id)})
    class_repo = FakeAcademicClassRepository({(class_id, tenant_id)})
    option_repo = FakeAcademicOptionRepository(set())
    class_opt_repo = FakeClassOptionRepository(set())

    use_case = CreateStudentAssignment(
        assign_repo, student_repo, class_repo, year_repo, option_repo, class_opt_repo,
    )

    assignment = use_case.execute(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_year_id=year_id,
        academic_class_id=class_id,
        created_by=created_by,
    )

    assert assignment.status is StudentAssignmentStatus.DRAFT
    assert assignment.closed_at is None
    assert assign_repo.find_by_id(assignment.id, tenant_id) is not None


def test_create_student_assignment_missing_student():
    tenant_id = uuid4()
    year_repo = FakeAcademicYearRepository()
    assign_repo = FakeStudentAssignmentRepository()
    student_repo = FakeStudentRepository(set())
    class_repo = FakeAcademicClassRepository(set())
    option_repo = FakeAcademicOptionRepository(set())
    class_opt_repo = FakeClassOptionRepository(set())

    use_case = CreateStudentAssignment(
        assign_repo, student_repo, class_repo, year_repo, option_repo, class_opt_repo,
    )

    with pytest.raises(ValueError, match="Eleve introuvable"):
        use_case.execute(tenant_id, uuid4(), uuid4(), uuid4(), uuid4())


def test_create_student_assignment_in_closed_year_rejected():
    tenant_id = uuid4()
    student_id = uuid4()
    class_id = uuid4()
    year_id = uuid4()

    year_repo = FakeAcademicYearRepository()
    year_repo.save(AcademicYear(year_id, tenant_id, "2026-2027", date(2026, 9, 1), date(2027, 7, 31), AcademicYearStatus.CLOSED))

    assign_repo = FakeStudentAssignmentRepository()
    student_repo = FakeStudentRepository({(student_id, tenant_id)})
    class_repo = FakeAcademicClassRepository({(class_id, tenant_id)})
    option_repo = FakeAcademicOptionRepository(set())
    class_opt_repo = FakeClassOptionRepository(set())

    use_case = CreateStudentAssignment(
        assign_repo, student_repo, class_repo, year_repo, option_repo, class_opt_repo,
    )

    with pytest.raises(ValueError, match="annee cloturee"):
        use_case.execute(tenant_id, student_id, year_id, class_id, uuid4())


def test_create_student_assignment_invalid_option():
    tenant_id = uuid4()
    student_id = uuid4()
    class_id = uuid4()
    year_id = uuid4()
    option_id = uuid4()

    year_repo = FakeAcademicYearRepository()
    year_repo.save(AcademicYear(year_id, tenant_id, "2026-2027", date(2026, 9, 1), date(2027, 7, 31), AcademicYearStatus.ACTIVE))

    assign_repo = FakeStudentAssignmentRepository()
    student_repo = FakeStudentRepository({(student_id, tenant_id)})
    class_repo = FakeAcademicClassRepository({(class_id, tenant_id)})
    option_repo = FakeAcademicOptionRepository({(option_id, tenant_id)})
    class_opt_repo = FakeClassOptionRepository(set())  # not linked to class!

    use_case = CreateStudentAssignment(
        assign_repo, student_repo, class_repo, year_repo, option_repo, class_opt_repo,
    )

    with pytest.raises(ValueError, match="L'option n'est pas associee a cette classe"):
        use_case.execute(tenant_id, student_id, year_id, class_id, uuid4(), option_id)


# =========================================================================
# Tests ChangeStudentAssignmentStatus
# =========================================================================

def test_activate_assignment_requires_active_year():
    tenant_id = uuid4()
    student_id = uuid4()
    year_id = uuid4()
    now = datetime.now(timezone.utc)

    year_repo = FakeAcademicYearRepository()
    # Year is DRAFT, not ACTIVE
    year_repo.save(AcademicYear(year_id, tenant_id, "2026-2027", date(2026, 9, 1), date(2027, 7, 31), AcademicYearStatus.DRAFT))

    assignment = StudentAssignment(
        id=uuid4(),
        tenant_id=tenant_id,
        student_id=student_id,
        academic_year_id=year_id,
        academic_class_id=uuid4(),
        academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT,
        created_by=uuid4(),
        created_at=now,
        updated_at=now,
    )
    assign_repo = FakeStudentAssignmentRepository()
    assign_repo.save(assignment)

    use_case = ChangeStudentAssignmentStatus(assign_repo, year_repo)

    with pytest.raises(ValueError, match="annee scolaire active"):
        use_case.activate(assignment.id, tenant_id)


def test_activate_assignment_prevents_multiple_active_for_student_in_same_year():
    tenant_id = uuid4()
    student_id = uuid4()
    year_id = uuid4()
    now = datetime.now(timezone.utc)

    year_repo = FakeAcademicYearRepository()
    year_repo.save(AcademicYear(year_id, tenant_id, "2026-2027", date(2026, 9, 1), date(2027, 7, 31), AcademicYearStatus.ACTIVE))

    assign_repo = FakeStudentAssignmentRepository()
    existing_active = StudentAssignment(
        id=uuid4(),
        tenant_id=tenant_id,
        student_id=student_id,
        academic_year_id=year_id,
        academic_class_id=uuid4(),
        academic_option_id=None,
        status=StudentAssignmentStatus.ACTIVE,
        created_by=uuid4(),
        created_at=now,
        updated_at=now,
    )
    draft_assignment = StudentAssignment(
        id=uuid4(),
        tenant_id=tenant_id,
        student_id=student_id,
        academic_year_id=year_id,
        academic_class_id=uuid4(),
        academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT,
        created_by=uuid4(),
        created_at=now,
        updated_at=now,
    )
    assign_repo.save(existing_active)
    assign_repo.save(draft_assignment)

    use_case = ChangeStudentAssignmentStatus(assign_repo, year_repo)

    with pytest.raises(ActiveConflictError, match="Une affectation active existe deja"):
        use_case.activate(draft_assignment.id, tenant_id)


def test_cancel_draft_assignment_and_close_active_assignment():
    tenant_id = uuid4()
    student_id = uuid4()
    year_id = uuid4()
    now = datetime.now(timezone.utc)

    year_repo = FakeAcademicYearRepository()
    year_repo.save(AcademicYear(year_id, tenant_id, "2026-2027", date(2026, 9, 1), date(2027, 7, 31), AcademicYearStatus.ACTIVE))

    assign_repo = FakeStudentAssignmentRepository()
    draft = StudentAssignment(
        id=uuid4(), tenant_id=tenant_id, student_id=student_id,
        academic_year_id=year_id, academic_class_id=uuid4(), academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT, created_by=uuid4(), created_at=now, updated_at=now,
    )
    assign_repo.save(draft)

    use_case = ChangeStudentAssignmentStatus(assign_repo, year_repo)

    cancelled = use_case.cancel(draft.id, tenant_id)
    assert cancelled.status is StudentAssignmentStatus.CANCELLED
    assert cancelled.closed_at is not None

    # Cannot activate cancelled
    with pytest.raises(ValueError, match="brouillon"):
        use_case.activate(draft.id, tenant_id)

    # Now create active assignment and close it
    active = StudentAssignment(
        id=uuid4(), tenant_id=tenant_id, student_id=student_id,
        academic_year_id=year_id, academic_class_id=uuid4(), academic_option_id=None,
        status=StudentAssignmentStatus.ACTIVE, created_by=uuid4(), created_at=now, updated_at=now,
    )
    assign_repo.save(active)

    closed = use_case.close(active.id, tenant_id)
    assert closed.status is StudentAssignmentStatus.CLOSED
    assert closed.closed_at is not None

    # Cannot activate closed
    with pytest.raises(ValueError, match="brouillon"):
        use_case.activate(active.id, tenant_id)
