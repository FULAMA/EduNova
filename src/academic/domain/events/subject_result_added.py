from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class SubjectResultAdded(DomainEvent):
    tenant_id: UUID
    student_id: UUID
    academic_period_id: UUID
    subject_id: UUID
    average: float
    coefficient: float
    record_version: int

    @classmethod
    def create(
        cls,
        occurred_at: datetime,
        tenant_id: UUID,
        student_id: UUID,
        academic_period_id: UUID,
        subject_id: UUID,
        average: float,
        coefficient: float,
        record_version: int,
    ) -> "SubjectResultAdded":
        return cls(
            event_id=uuid4(),
            occurred_at=occurred_at,
            tenant_id=tenant_id,
            student_id=student_id,
            academic_period_id=academic_period_id,
            subject_id=subject_id,
            average=average,
            coefficient=coefficient,
            record_version=record_version,
        )
