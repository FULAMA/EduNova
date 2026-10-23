from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ValidateAcademicRecordRequest:
    tenant_id: UUID
    student_id: UUID
    academic_period_id: UUID
    expected_version: int
