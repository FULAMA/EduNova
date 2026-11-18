from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class TeacherAssignment:
    tenant_id: UUID
    teacher_user_id: UUID
    academic_class_id: UUID
    subject_id: UUID
    academic_year_id: UUID
    assigned_by: UUID
    assigned_at: datetime

    def __post_init__(self) -> None:
        for val, name in (
            (self.tenant_id, "tenant_id"),
            (self.teacher_user_id, "teacher_user_id"),
            (self.academic_class_id, "academic_class_id"),
            (self.subject_id, "subject_id"),
            (self.academic_year_id, "academic_year_id"),
            (self.assigned_by, "assigned_by"),
        ):
            if not isinstance(val, UUID):
                raise TypeError(f"L'identifiant {name} doit etre un UUID.")
        if not isinstance(self.assigned_at, datetime):
            raise TypeError("assigned_at doit etre une date/heure valide.")
