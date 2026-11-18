from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.presentation.api.schemas.student import StudentSummaryResponse


class LinkParentStudentRequest(BaseModel):
    parent_user_id: UUID
    student_id: UUID
    relationship_type: str = Field(..., description="Lien de parenté : FATHER, MOTHER, LEGAL_GUARDIAN")


class ParentStudentLinkResponse(BaseModel):
    tenant_id: UUID
    parent_user_id: UUID
    student_id: UUID
    relationship_type: str
    created_by: UUID
    created_at: datetime


class ParentChildResponse(BaseModel):
    student: StudentSummaryResponse
    relationship_type: str
