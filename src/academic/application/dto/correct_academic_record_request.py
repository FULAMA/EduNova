from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CorrectAcademicRecordRequest:
    tenant_id: UUID
    student_id: UUID
    academic_period_id: UUID
    expected_version: int
    actor_id: UUID
    reason: str
    general_average: float
    failed_subjects: int
    credits_obtained: float
