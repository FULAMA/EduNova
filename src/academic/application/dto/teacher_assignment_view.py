from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class TeacherAssignmentView:
    tenant_id: UUID
    teacher_user_id: UUID
    academic_class_id: UUID
    academic_class_label: str | None
    subject_id: UUID
    subject_label: str | None
    academic_year_id: UUID
    academic_year_label: str | None
    assigned_by: UUID
    assigned_at: datetime
