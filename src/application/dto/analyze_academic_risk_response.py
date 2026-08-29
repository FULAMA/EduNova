from dataclasses import dataclass
from typing import Tuple

from src.domain.value_objects.academic_risk import RiskLevel


@dataclass(frozen=True)
class AnalyzeAcademicRiskResponse:
    level: RiskLevel
    score: int
    reasons: Tuple[str, ...]