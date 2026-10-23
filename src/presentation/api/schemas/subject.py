from uuid import UUID
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class SubjectInput(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    name: str = Field(min_length=1)
    code: str = Field(min_length=1)
    coefficient: float = Field(gt=0)


class SubjectUpdateInput(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    name: str = Field(min_length=1)
    code: str = Field(min_length=1)


class SubjectResponse(BaseModel):
    id: UUID
    name: str
    code: str
    coefficient: float
    active: bool


class AcademicPeriodResponse(BaseModel):
    id: UUID
    name: str
    start_date: date
    end_date: date
    academic_year_id: UUID | None = None


class AcademicPeriodInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    academic_year_id: UUID
    name: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date
