from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ClassOption:
    id: UUID
    academic_class_id: UUID
    academic_option_id: UUID
    active: bool = True
