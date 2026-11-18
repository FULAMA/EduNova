from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AssignTeacherInput(BaseModel):
    teacher_user_id: UUID = Field(..., description="Identifiant du compte utilisateur enseignant")
    academic_class_id: UUID = Field(..., description="Identifiant de la classe cible")
    subject_id: UUID = Field(..., description="Identifiant de la matière affectée")
    academic_year_id: UUID = Field(..., description="Identifiant de l'année scolaire")


class TeacherAssignmentResponse(BaseModel):
    tenant_id: UUID
    teacher_user_id: UUID
    academic_class_id: UUID
    subject_id: UUID
    academic_year_id: UUID
    assigned_by: UUID
    assigned_at: datetime
