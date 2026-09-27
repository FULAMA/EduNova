from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SubjectResultResponse:
    subject_id: UUID
    average: float
    coefficient: float
