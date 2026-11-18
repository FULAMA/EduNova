from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class GradeDisputeStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class GradeDispute:
    id: UUID
    tenant_id: UUID
    student_id: UUID
    academic_period_id: UUID
    subject_id: UUID
    reason: str
    status: GradeDisputeStatus
    submitted_by: UUID
    submitted_at: datetime
    reviewed_by: UUID | None = None
    reviewed_at: datetime | None = None
    resolution_notes: str | None = None
    resolved_at: datetime | None = None

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        student_id: UUID,
        academic_period_id: UUID,
        subject_id: UUID,
        reason: str,
        submitted_by: UUID,
    ) -> "GradeDispute":
        clean_reason = reason.strip()
        if not clean_reason:
            raise ValueError("Le motif de la contestation est obligatoire.")

        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            student_id=student_id,
            academic_period_id=academic_period_id,
            subject_id=subject_id,
            reason=clean_reason,
            status=GradeDisputeStatus.SUBMITTED,
            submitted_by=submitted_by,
            submitted_at=now,
        )

    def start_review(self, reviewer_id: UUID) -> "GradeDispute":
        if self.status != GradeDisputeStatus.SUBMITTED:
            raise ValueError("Seule une contestation au statut SUBMITTED peut etre mise sous examen.")

        now = datetime.now(timezone.utc)
        return GradeDispute(
            id=self.id,
            tenant_id=self.tenant_id,
            student_id=self.student_id,
            academic_period_id=self.academic_period_id,
            subject_id=self.subject_id,
            reason=self.reason,
            status=GradeDisputeStatus.UNDER_REVIEW,
            submitted_by=self.submitted_by,
            submitted_at=self.submitted_at,
            reviewed_by=reviewer_id,
            reviewed_at=now,
            resolution_notes=self.resolution_notes,
            resolved_at=self.resolved_at,
        )

    def resolve(self, decision: GradeDisputeStatus, resolution_notes: str, reviewer_id: UUID) -> "GradeDispute":
        if self.status not in (GradeDisputeStatus.SUBMITTED, GradeDisputeStatus.UNDER_REVIEW):
            raise ValueError("Cette contestation a deja ete resolue.")

        if decision not in (GradeDisputeStatus.ACCEPTED, GradeDisputeStatus.REJECTED):
            raise ValueError("La decision de resolution doit etre ACCEPTED ou REJECTED.")

        clean_notes = resolution_notes.strip()
        if not clean_notes:
            raise ValueError("Le motif de decision (notes de resolution) est obligatoire.")

        now = datetime.now(timezone.utc)
        return GradeDispute(
            id=self.id,
            tenant_id=self.tenant_id,
            student_id=self.student_id,
            academic_period_id=self.academic_period_id,
            subject_id=self.subject_id,
            reason=self.reason,
            status=decision,
            submitted_by=self.submitted_by,
            submitted_at=self.submitted_at,
            reviewed_by=reviewer_id,
            reviewed_at=self.reviewed_at or now,
            resolution_notes=clean_notes,
            resolved_at=now,
        )
