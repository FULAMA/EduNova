from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AddSubjectResultResponse:
    student_id: UUID
    academic_period_id: UUID
    subject_id: UUID
    average: float
    coefficient: float
    general_average: float
    failed_subjects: int
