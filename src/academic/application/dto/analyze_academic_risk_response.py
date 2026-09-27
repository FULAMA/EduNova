from dataclasses import dataclass


@dataclass(frozen=True)
class AnalyzeAcademicRiskResponse:
    level: str
    score: int
    reasons: tuple[str, ...]
