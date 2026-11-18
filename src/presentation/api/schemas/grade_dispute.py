from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.academic.domain.entities.grade_dispute import GradeDisputeStatus


class CreateGradeDisputeRequest(BaseModel):
    student_id: UUID
    academic_period_id: UUID
    subject_id: UUID
    reason: str = Field(..., min_length=5, max_length=1000, description="Motif clair de la réclamation")


class ResolveGradeDisputeRequest(BaseModel):
    decision: GradeDisputeStatus = Field(..., description="ACCEPTED ou REJECTED")
    resolution_notes: str = Field(..., min_length=5, max_length=1000, description="Motivation de la décision")


class GradeDisputeResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    student_id: UUID
    academic_period_id: UUID
    subject_id: UUID
    reason: str
    status: GradeDisputeStatus
    submitted_by: UUID
    submitted_at: datetime
    reviewed_by: UUID | None = None
    reviewed_at: datetime | None = None
    resolution_notes: str | None = None
    resolved_at: datetime | None = None
