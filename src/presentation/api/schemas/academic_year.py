from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from src.academic.domain.entities.academic_year import AcademicYearStatus


class AcademicYearInput(BaseModel):
    label: str = Field(min_length=9, max_length=9)
    start_date: date
    end_date: date


class AcademicYearResponse(BaseModel):
    id: UUID
    label: str
    start_date: date
    end_date: date
    status: AcademicYearStatus
