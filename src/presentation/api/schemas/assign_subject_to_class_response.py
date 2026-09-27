from uuid import UUID

from pydantic import BaseModel


class AssignSubjectToClassResponseSchema(BaseModel):
    id: UUID
    academic_class_id: UUID
    subject_id: UUID
    coefficient: float
    academic_option_id: UUID | None
    active: bool
