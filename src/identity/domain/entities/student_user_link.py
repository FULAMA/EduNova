from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class StudentUserLink:
    tenant_id: UUID
    user_id: UUID
    student_id: UUID
    created_by: UUID
    created_at: datetime

