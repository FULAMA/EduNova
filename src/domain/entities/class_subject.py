from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ClassSubject:
    id: UUID
    tenant_id: UUID
    academic_class_id: UUID
    subject_id: UUID
    coefficient: float
    academic_option_id: UUID | None = None
    active: bool = True

    def __post_init__(self):
        if self.tenant_id is None:
            raise ValueError("Le tenant est obligatoire.")

        if self.coefficient <= 0:
            raise ValueError("Le coefficient doit être supérieur à zéro.")