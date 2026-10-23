from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone
from typing import cast
from uuid import UUID, uuid4

import pytest

from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus
from src.academic.domain.entities.student_assignment import (
    StudentAssignment,
    StudentAssignmentStatus,
)


def test_academic_year_has_explicit_lifecycle() -> None:
    year = AcademicYear(
        id=uuid4(),
        tenant_id=uuid4(),
        label='2026-2027',
        start_date=date(2026, 9, 1),
        end_date=date(2027, 7, 31),
    )

    assert year.status is AcademicYearStatus.DRAFT
    year = year.activate()
    assert year.status is AcademicYearStatus.ACTIVE
    assert year.close().status is AcademicYearStatus.CLOSED


@pytest.mark.parametrize(
    ("start_date", "end_date"),
    [
        (date(2026, 9, 1), date(2026, 9, 1)),
        (date(2027, 7, 31), date(2026, 9, 1)),
    ],
)
def test_academic_year_rejects_invalid_dates(start_date: date, end_date: date) -> None:
    with pytest.raises(ValueError, match="date de fin"):
        AcademicYear(uuid4(), uuid4(), "2026-2027", start_date, end_date)


def test_academic_year_rejects_invalid_types_and_transitions() -> None:
    with pytest.raises(TypeError, match="UUID"):
        AcademicYear(cast(UUID, "year-1"), uuid4(), "2026-2027", date(2026, 9, 1), date(2027, 7, 31))

    active = AcademicYear(
        uuid4(), uuid4(), "2026-2027", date(2026, 9, 1), date(2027, 7, 31),
    ).activate()
    with pytest.raises(ValueError, match="brouillon"):
        active.activate()
    with pytest.raises(ValueError, match="active"):
        active.close().close()


def make_assignment(
    status: StudentAssignmentStatus = StudentAssignmentStatus.DRAFT,
    closed_at: datetime | None = None,
) -> StudentAssignment:
    now = datetime.now(timezone.utc)
    return StudentAssignment(
        id=uuid4(),
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_year_id=uuid4(),
        academic_class_id=uuid4(),
        academic_option_id=None,
        status=status,
        created_by=uuid4(),
        created_at=now,
        updated_at=now,
        closed_at=closed_at,
    )


def test_assignment_requires_coherent_closed_at() -> None:
    with pytest.raises(ValueError, match="date de cloture"):
        make_assignment(StudentAssignmentStatus.ACTIVE, datetime.now(timezone.utc))

    with pytest.raises(ValueError, match="date de cloture"):
        make_assignment(StudentAssignmentStatus.CLOSED)


def test_assignment_preserves_allowed_transitions_and_immutability() -> None:
    draft = make_assignment()
    active = draft.activate()
    closed = active.close()
    cancelled = draft.cancel()

    assert draft.status is StudentAssignmentStatus.DRAFT
    assert active.status is StudentAssignmentStatus.ACTIVE
    assert active.closed_at is None
    assert closed.status is StudentAssignmentStatus.CLOSED
    assert closed.closed_at is not None
    assert cancelled.status is StudentAssignmentStatus.CANCELLED
    assert cancelled.closed_at is not None

    with pytest.raises(ValueError, match="brouillon"):
        closed.activate()
    with pytest.raises(ValueError, match="active"):
        closed.close()
    with pytest.raises(FrozenInstanceError):
        draft.status = StudentAssignmentStatus.ACTIVE  # type: ignore[misc]


def test_closed_assignment_cannot_be_reopened() -> None:
    assignment = StudentAssignment(
        id=uuid4(),
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_year_id=uuid4(),
        academic_class_id=uuid4(),
        academic_option_id=None,
        status=StudentAssignmentStatus.DRAFT,
        created_by=uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    ).activate().close()

    with pytest.raises(ValueError, match='brouillon'):
        assignment.activate()


def test_cancelled_assignment_cannot_be_reopened_or_closed() -> None:
    draft = make_assignment()
    cancelled = draft.cancel()

    with pytest.raises(ValueError, match="brouillon"):
        cancelled.activate()

    with pytest.raises(ValueError, match="active"):
        cancelled.close()

    with pytest.raises(ValueError, match="brouillon"):
        cancelled.cancel()


def test_academic_year_immutability_and_forbidden_transitions() -> None:
    year = AcademicYear(
        id=uuid4(),
        tenant_id=uuid4(),
        label="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 7, 31),
    )

    with pytest.raises(FrozenInstanceError):
        year.status = AcademicYearStatus.ACTIVE  # type: ignore[misc]

    # DRAFT cannot be closed directly
    with pytest.raises(ValueError, match="active"):
        year.close()

    active = year.activate()
    # ACTIVE cannot be activated again
    with pytest.raises(ValueError, match="brouillon"):
        active.activate()

    closed = active.close()
    # CLOSED cannot be activated or closed again
    with pytest.raises(ValueError, match="brouillon"):
        closed.activate()
    with pytest.raises(ValueError, match="active"):
        closed.close()


def test_assignment_cannot_cancel_active_or_closed() -> None:
    draft = make_assignment()
    active = draft.activate()
    closed = active.close()

    with pytest.raises(ValueError, match="brouillon"):
        active.cancel()

    with pytest.raises(ValueError, match="brouillon"):
        closed.cancel()

