from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ReportCardResponse(BaseModel):
    id: UUID
    student_id: UUID
    academic_period_id: UUID
    deliberation_id: UUID
    deliberation_version: int
    record_version: int
    report_version: int
    status: str
    snapshot: dict[str, Any]
    snapshot_hash: str
    created_at: datetime | None
    issued_at: datetime | None


class PrepareReportCardRequest(BaseModel):
    deliberation_id: UUID
