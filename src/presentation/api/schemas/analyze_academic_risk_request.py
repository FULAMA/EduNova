from pydantic import BaseModel, ConfigDict, Field


class AnalyzeAcademicRiskRequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    average: float = Field(ge=0, le=20)
    attendance_rate: float = Field(ge=0, le=100)
    unjustified_absences: int = Field(ge=0)
