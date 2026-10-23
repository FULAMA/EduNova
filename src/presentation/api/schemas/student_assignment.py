from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.academic.domain.entities.student_assignment import StudentAssignmentStatus


class StudentAssignmentInput(BaseModel):
    student_id: UUID
    academic_year_id: UUID
    academic_class_id: UUID
    academic_option_id: UUID | None = None


class StudentPromotionInput(BaseModel):
    source_assignment_id: UUID
    deliberation_id: UUID
    target_year_id: UUID
    target_class_id: UUID


class StudentAssignmentResponse(BaseModel):
    id: UUID
    student_id: UUID
    academic_year_id: UUID
    academic_class_id: UUID
    academic_option_id: UUID | None
    status: StudentAssignmentStatus
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
