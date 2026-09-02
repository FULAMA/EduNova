from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AssignSubjectToClassRequest:
    academic_class_id: UUID
    subject_id: UUID
    coefficient: float
    academic_option_id: UUID | None = None
