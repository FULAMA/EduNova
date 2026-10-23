from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
import hashlib
import json
from typing import Any
from uuid import UUID


class ReportCardStatus(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    SUPERSEDED = "SUPERSEDED"


@dataclass(frozen=True)
class ReportCard:
    tenant_id: UUID
    student_id: UUID
    academic_period_id: UUID
    deliberation_id: UUID
    deliberation_version: int
    record_version: int
    report_version: int
    snapshot: dict[str, Any]
    snapshot_hash: str
    status: ReportCardStatus = ReportCardStatus.DRAFT
    id: UUID | None = None
    created_at: datetime | None = None
    issued_at: datetime | None = None
    issued_by: UUID | None = None
    previous_report_card_id: UUID | None = None

    def __post_init__(self) -> None:
        for value, label in (
            (self.tenant_id, "tenant"),
            (self.student_id, "eleve"),
            (self.academic_period_id, "periode"),
            (self.deliberation_id, "deliberation"),
        ):
            if not isinstance(value, UUID):
                raise TypeError(f"L identifiant {label} doit etre un UUID.")
        if self.deliberation_version <= 0 or self.record_version <= 0:
            raise ValueError("Les versions sources doivent etre positives.")
        if self.report_version <= 0:
            raise ValueError("La version du bulletin doit etre positive.")
        if not self.snapshot:
            raise ValueError("Le snapshot du bulletin ne peut pas etre vide.")
        if not self.snapshot_hash:
            raise ValueError("Le hash du snapshot est obligatoire.")
        if self.status is ReportCardStatus.ISSUED and (
            self.issued_at is None or self.issued_by is None
        ):
            raise ValueError("Un bulletin emis doit avoir un auteur et une date.")

    def publish(self, actor_id: UUID, published_at: datetime) -> "ReportCard":
        if self.status is not ReportCardStatus.DRAFT:
            raise ValueError("Seul un bulletin prepare peut etre emis.")
        return replace(
            self,
            status=ReportCardStatus.ISSUED,
            issued_at=published_at,
            issued_by=actor_id,
        )

    @staticmethod
    def calculate_snapshot_hash(snapshot: dict[str, Any]) -> str:
        canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
