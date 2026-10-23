from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.shared.domain.events.domain_event import DomainEvent


def test_domain_event_preserves_event_id_and_occurred_at() -> None:
    event_id = uuid4()
    occurred_at = datetime(2026, 9, 27, 12, 0, tzinfo=timezone.utc)

    event = DomainEvent(
        event_id=event_id,
        occurred_at=occurred_at,
    )

    assert event.event_id == event_id
    assert event.occurred_at == occurred_at


def test_domain_event_is_immutable() -> None:
    event = DomainEvent(
        event_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
    )

    with pytest.raises(AttributeError):
        event.occurred_at = datetime.now(timezone.utc)  # type: ignore[misc]


def test_domain_event_is_a_frozen_dataclass() -> None:
    event = DomainEvent(
        event_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
    )

    with pytest.raises(AttributeError):
        event.event_id = uuid4()  # type: ignore[misc]

def test_domain_event_event_id_is_a_uuid() -> None:
    event_id = uuid4()
    event = DomainEvent(
        event_id=event_id,
        occurred_at=datetime.now(timezone.utc),
    )

    assert isinstance(event.event_id, type(event_id))


def test_subject_result_added_generates_unique_event_ids() -> None:
    from src.academic.domain.events.subject_result_added import SubjectResultAdded

    occurred_at = datetime.now(timezone.utc)

    event_a = SubjectResultAdded.create(
        occurred_at=occurred_at,
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_id=uuid4(),
        average=15.0,
        coefficient=2.0,
        record_version=1,
    )

    event_b = SubjectResultAdded.create(
        occurred_at=occurred_at,
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_id=uuid4(),
        average=15.0,
        coefficient=2.0,
        record_version=1,
    )

    assert event_a.event_id != event_b.event_id


def test_domain_event_preserves_timezone_aware_occurred_at() -> None:
    occurred_at = datetime(
        2026,
        9,
        28,
        12,
        30,
        tzinfo=timezone.utc,
    )

    event = DomainEvent(
        event_id=uuid4(),
        occurred_at=occurred_at,
    )

    assert event.occurred_at == occurred_at
    assert event.occurred_at.tzinfo == timezone.utc


def test_domain_event_currently_accepts_naive_occurred_at() -> None:
    occurred_at = datetime(2026, 9, 28, 12, 30)

    event = DomainEvent(
        event_id=uuid4(),
        occurred_at=occurred_at,
    )

    assert event.occurred_at == occurred_at
    assert event.occurred_at.tzinfo is None
