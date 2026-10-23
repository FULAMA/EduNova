from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class StudentSummary:
    id: UUID
    first_name: str
    last_name: str
    email: str | None
    active: bool
