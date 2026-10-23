from uuid import UUID, uuid4

from datetime import datetime, timezone

import pytest

from src.academic.application.dto.add_subject_result_request import (
    AddSubjectResultRequest,
)
from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.application.use_cases.add_subject_result import AddSubjectResult
from src.academic.domain.entities.student_academic_record import StudentAcademicRecord
from src.academic.domain.events.subject_result_added import SubjectResultAdded
from src.shared.domain.events.domain_event import DomainEvent
from tests.support.academic_eligibility import eligible_result_repositories
from src.shared.application.events.event_handler import EventHandler
from src.shared.application.events.in_memory_event_dispatcher import (
    InMemoryEventDispatcher,
)


class FakeAcademicRecordRepository(StudentAcademicRecordRepository):
    def __init__(self) -> None:
        self.records: dict[
            tuple[UUID, UUID, UUID],
            StudentAcademicRecord,
        ] = {}

    def save(
        self,
        record: StudentAcademicRecord,
        *,
        expected_version: int | None = None,
        operation: str = "SAVE",
    ) -> None:
        key = (
            record.tenant_id,
            record.student_id,
            record.academic_period_id,
        )
        self.records[key] = record

    def find_by_student(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> StudentAcademicRecord | None:
        for record in self.records.values():
            if (
                record.student_id == student_id
                and record.tenant_id == tenant_id
            ):
                return record
        return None

    def find_by_student_and_period(
        self,
        student_id: UUID,
        academic_period_id: UUID,
        tenant_id: UUID,
    ) -> StudentAcademicRecord | None:
        return self.records.get(
            (tenant_id, student_id, academic_period_id)
        )


class RecordingHandler(EventHandler):
    def __init__(self) -> None:
        self.events: list[SubjectResultAdded] = []

    def handle(self, event: DomainEvent) -> None:
        if isinstance(event, SubjectResultAdded):
            self.events.append(event)


def create_record() -> StudentAcademicRecord:
    return StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(),
        general_average=0,
        failed_subjects=0,
        credits_obtained=0,
        total_credits=30,
    )


def test_subject_result_added_event_reaches_registered_handler():
    repository = FakeAcademicRecordRepository()
    dispatcher = InMemoryEventDispatcher()
    handler = RecordingHandler()

    dispatcher.register(SubjectResultAdded, handler)

    record = create_record()
    repository.save(record)

    subject_id = uuid4()
    use_case = AddSubjectResult(repository, dispatcher, **eligible_result_repositories([subject_id]))

    response = use_case.execute(
        AddSubjectResultRequest(
            tenant_id=record.tenant_id,
            student_id=record.student_id,
            academic_period_id=record.academic_period_id,
            subject_id=subject_id,
            average=15.0,
            coefficient=2.0,
        )
    )

    assert response.subject_id == subject_id
    assert len(handler.events) == 1

    event = handler.events[0]

    assert event.tenant_id == record.tenant_id
    assert event.student_id == record.student_id
    assert event.academic_period_id == record.academic_period_id
    assert event.subject_id == subject_id
    assert event.average == 15.0
    assert event.coefficient == 2.0
    assert event.record_version == 2


def test_subject_result_event_without_handlers_is_a_noop():
    dispatcher = InMemoryEventDispatcher()
    dispatcher.dispatch(SubjectResultAdded.create(
        occurred_at=datetime.now(timezone.utc),
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_id=uuid4(),
        average=15.0,
        coefficient=2.0,
        record_version=2,
    ))


def test_handler_failure_occurs_after_subject_result_is_saved():
    class FailingHandler(EventHandler):
        def handle(self, event: DomainEvent) -> None:
            raise RuntimeError("consumer unavailable")

    repository = FakeAcademicRecordRepository()
    dispatcher = InMemoryEventDispatcher()
    dispatcher.register(SubjectResultAdded, FailingHandler())
    record = create_record()
    repository.save(record)

    subject_id = uuid4()
    use_case = AddSubjectResult(repository, dispatcher, **eligible_result_repositories([subject_id]))
    with pytest.raises(RuntimeError, match="consumer unavailable"):
        use_case.execute(AddSubjectResultRequest(
            tenant_id=record.tenant_id,
            student_id=record.student_id,
            academic_period_id=record.academic_period_id,
            subject_id=subject_id,
            average=15.0,
            coefficient=2.0,
        ))

    persisted = repository.find_by_student_and_period(
        record.student_id,
        record.academic_period_id,
        record.tenant_id,
    )
    assert persisted is not None
    assert len(persisted.subject_results) == 1
    assert persisted.version == 2






