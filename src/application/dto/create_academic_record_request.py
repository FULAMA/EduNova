from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateAcademicRecordRequest:
    tenant_id: UUID
    student_id: UUID
    academic_period_id: UUID
    total_credits: float