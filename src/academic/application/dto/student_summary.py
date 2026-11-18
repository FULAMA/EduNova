from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class StudentDuplicateCandidate:
    id: UUID
    first_name: str
    last_name: str
    registration_number: str | None = None


@dataclass(frozen=True)
class StudentSummary:
    id: UUID
    first_name: str
    last_name: str
    email: str | None
    active: bool
    registration_number: str | None = None
    potential_duplicates: tuple[StudentDuplicateCandidate, ...] = ()
