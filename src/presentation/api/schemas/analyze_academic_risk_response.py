from pydantic import BaseModel


class AnalyzeAcademicRiskResponseSchema(BaseModel):
    level: str
    score: int
    reasons: list[str]
