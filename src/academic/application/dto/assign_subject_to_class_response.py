from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AssignSubjectToClassResponse:
    id: UUID
    academic_class_id: UUID
    subject_id: UUID
    coefficient: float
    academic_option_id: UUID | None
    active: bool
