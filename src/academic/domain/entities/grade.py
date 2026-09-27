from dataclasses import dataclass
from uuid import UUID

from src.academic.domain.entities.assessment import Assessment
from src.academic.domain.value_objects.score import Score


@dataclass(frozen=True)
class Grade:
    id: UUID
    student_id: UUID
    assessment: Assessment
    score: Score

    def normalized_score(self) -> float:
        return self.score.normalized_to_20()
