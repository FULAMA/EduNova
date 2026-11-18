"""
MissingGrade Value Object - Domain Layer

Represents a missing grade (not recorded) which is distinct from a zero grade.
This implements D6: "Une note manquante est distincte d'un zero".

In the academic domain:
- A Grade with value=0 means the student explicitly scored zero
- A MissingGrade means the grade was not recorded (absent, not submitted, etc.)
- These two concepts must be treated differently in calculations
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from uuid import UUID

from src.academic.domain.value_objects.score import Score


class MissingGradeReason(str, Enum):
    """Reason why a grade is missing."""
    ABSENT = "ABSENT"
    NOT_SUBMITTED = "NOT_SUBMITTED"
    EXEMPTED = "EXEMPTED"
    TECHNICAL_ISSUE = "TECHNICAL_ISSUE"
    OTHER = "OTHER"


@dataclass(frozen=True)
class MissingGrade:
    """
    Represents a missing grade (not recorded).
    
    This value object is used to explicitly represent the absence of a grade,
    which is distinct from a zero grade as per D6.
    
    When calculating averages:
    - Missing grades should NOT be counted as zero (D6)
    - Missing grades should either be excluded from the calculation or
      handled according to the establishment's policy
    
    Invariants:
    - A MissingGrade cannot have a numeric value (it represents absence)
    - A MissingGrade must have a reason
    - A MissingGrade is immutable
    """
    reason: MissingGradeReason
    recorded_by: UUID | None = None
    recorded_date: date | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate invariants."""
        if not isinstance(self.reason, MissingGradeReason):
            raise TypeError("La raison de l'absence de note est invalide.")
        
        if self.recorded_by is not None and not isinstance(self.recorded_by, UUID):
            raise TypeError("L'identifiant de l'utilisateur doit etre un UUID.")
        
        if self.recorded_date is not None and not isinstance(self.recorded_date, date):
            raise TypeError("La date d'enregistrement doit etre une date.")

    @property
    def is_absent(self) -> bool:
        """Check if the missing grade is due to absence."""
        return self.reason == MissingGradeReason.ABSENT

    @property
    def is_exempted(self) -> bool:
        """Check if the student was exempted from this assessment."""
        return self.reason == MissingGradeReason.EXEMPTED

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "reason": self.reason.value,
            "recorded_by": str(self.recorded_by) if self.recorded_by else None,
            "recorded_date": self.recorded_date.isoformat() if self.recorded_date else None,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MissingGrade":
        """Create a MissingGrade from a dictionary."""
        return cls(
            reason=MissingGradeReason(data["reason"]),
            recorded_by=UUID(data["recorded_by"]) if data.get("recorded_by") else None,
            recorded_date=date.fromisoformat(data["recorded_date"]) if data.get("recorded_date") else None,
            notes=data.get("notes"),
        )


# Type alias for grades that can be either a numeric grade or a missing grade
# This allows the domain to explicitly represent the D6 distinction
GradeValue = Score | MissingGrade
