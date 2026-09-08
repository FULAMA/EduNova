from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ClassOption:
    id: UUID
    tenant_id: UUID
    academic_class_id: UUID
    academic_option_id: UUID
    active: bool = True

    def __post_init__(self):
        if self.tenant_id is None:
            raise ValueError("Le tenant est obligatoire.")