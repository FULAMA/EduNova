from src.domain.value_objects.academic_risk import RiskLevel
from pydantic import BaseModel


class AnalyzeAcademicRiskResponseSchema(BaseModel):
    level: RiskLevel
    score: int
    reasons: list[str]
