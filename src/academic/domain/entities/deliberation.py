from dataclasses import dataclass
from enum import Enum
import math
from uuid import UUID
from datetime import datetime


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
    tenant_id: UUID | None = None
    academic_period_id: UUID | None = None
    record_version: int | None = None
    id: UUID | None = None
    status: str = "PREPARED"
    version: int = 1
    created_by: UUID | None = None
    created_at: datetime | None = None
    validated_by: UUID | None = None
    validated_at: datetime | None = None

    def __post_init__(self):
        if not math.isfinite(self.average) or self.average < 0:
            raise ValueError(
                "La moyenne de délibération ne peut pas être négative."
            )

        if self.failed_subjects < 0:
            raise ValueError(
                "Le nombre de matières échouées ne peut pas être négatif."
            )
        if self.tenant_id is not None and not isinstance(self.tenant_id, UUID):
            raise TypeError("Le tenant de la deliberation doit etre un UUID.")
        if self.academic_period_id is not None and not isinstance(self.academic_period_id, UUID):
            raise TypeError("La periode de la deliberation doit etre un UUID.")
        if self.record_version is not None and self.record_version <= 0:
            raise ValueError("La version du dossier doit etre superieure a zero.")
        if self.version <= 0:
            raise ValueError("La version de la deliberation doit etre superieure a zero.")
