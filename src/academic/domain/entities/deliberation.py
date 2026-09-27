from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class DeliberationDecision(str, Enum):
    ADMITTED = "ADMITTED"
    CONDITIONAL = "CONDITIONAL"
    FAILED = "FAILED"


@dataclass(frozen=True)
class Deliberation:
    student_id: UUID
    average: float
    failed_subjects: int
    decision: DeliberationDecision

    def __post_init__(self):
        if self.average < 0:
            raise ValueError(
                "La moyenne de délibération ne peut pas être négative."
            )

        if self.failed_subjects < 0:
            raise ValueError(
                "Le nombre de matières échouées ne peut pas être négatif."
            )
