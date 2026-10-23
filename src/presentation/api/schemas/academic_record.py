from uuid import UUID

from pydantic import BaseModel


class SubjectResultResponse(BaseModel):
    subject_id: UUID
    subject_name: str | None = None
    average: float
    coefficient: float


class AcademicRecordResponse(BaseModel):
    student_id: UUID
    academic_period_id: UUID
    general_average: float
    failed_subjects: int
    credits_obtained: float
    total_credits: float
    subject_results: list[SubjectResultResponse]
    status: str
    version: int
    academic_period_name: str | None = None


class DeliberationResponse(BaseModel):
    student_id: UUID
    academic_period_id: UUID
    record_version: int
    average: float
    failed_subjects: int
    decision: str
    deliberation_id: UUID | None = None
    deliberation_status: str = "PREPARED"
    deliberation_version: int = 1


class AcademicRecordHistoryResponse(BaseModel):
    version: int
    status: str
    operation: str
    recorded_at: str
    actor_id: UUID | None = None
    reason: str | None = None
    snapshot: dict


class EligibleAcademicPeriodResponse(BaseModel):
    id: UUID
    name: str
    academic_year_id: UUID
    academic_year_label: str
    has_record: bool


class EligibleSubjectResponse(BaseModel):
    id: UUID
    name: str
    coefficient: float
