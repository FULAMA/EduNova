from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AddSubjectResultRequest:
    tenant_id: UUID
    student_id: UUID
    academic_period_id: UUID
    subject_id: UUID
    average: float
    coefficient: float
