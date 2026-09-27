from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class AcademicRisk:
    level: RiskLevel
    score: int
    reasons: tuple[str, ...]

    def __post_init__(self):
        if not 0 <= self.score <= 100:
            raise ValueError(
                "Le score de risque doit être compris entre 0 et 100."
            )

        if not self.reasons:
            raise ValueError(
                "Un risque académique doit avoir au moins une raison."
            )