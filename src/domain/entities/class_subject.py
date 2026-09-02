from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ClassSubject:
    id: UUID
    academic_class_id: UUID
    subject_id: UUID
    coefficient: float
    academic_option_id: UUID | None = None
    active: bool = True

    def __post_init__(self):
        if self.coefficient <= 0:
            raise ValueError(
                "Le coefficient doit être supérieur à zéro."
            )
