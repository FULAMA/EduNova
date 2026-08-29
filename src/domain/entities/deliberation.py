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