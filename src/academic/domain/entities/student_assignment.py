from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class StudentAssignmentStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class StudentAssignment:
    id: UUID
    tenant_id: UUID
    student_id: UUID
    academic_year_id: UUID
    academic_class_id: UUID
    academic_option_id: UUID | None
    status: StudentAssignmentStatus
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None

    def __post_init__(self) -> None:
        identifiers = (
            self.id,
            self.tenant_id,
            self.student_id,
            self.academic_year_id,
            self.academic_class_id,
            self.created_by,
        )
        if not all(isinstance(identifier, UUID) for identifier in identifiers):
            raise TypeError("Les identifiants d'affectation doivent etre des UUID.")
        if self.academic_option_id is not None and not isinstance(self.academic_option_id, UUID):
            raise TypeError("L'identifiant de l'option doit etre un UUID.")
        if not isinstance(self.status, StudentAssignmentStatus):
            raise TypeError("Le statut de l'affectation est invalide.")
        if not isinstance(self.created_at, datetime) or not isinstance(self.updated_at, datetime):
            raise TypeError("Les dates de l'affectation doivent etre des datetime.")
        if self.closed_at is not None and not isinstance(self.closed_at, datetime):
            raise TypeError("La date de cloture doit etre un datetime.")

        closed_status = {
            StudentAssignmentStatus.CLOSED,
            StudentAssignmentStatus.CANCELLED,
        }
        if self.status in closed_status and self.closed_at is None:
            raise ValueError("Une affectation cloturee doit avoir une date de cloture.")
        if self.status not in closed_status and self.closed_at is not None:
            raise ValueError("Une affectation non cloturee ne peut pas avoir de date de cloture.")

    def activate(self) -> "StudentAssignment":
        if self.status is not StudentAssignmentStatus.DRAFT:
            raise ValueError("Seule une affectation brouillon peut etre activee.")
        return self._replace_status(StudentAssignmentStatus.ACTIVE)

    def cancel(self) -> "StudentAssignment":
        if self.status is not StudentAssignmentStatus.DRAFT:
            raise ValueError("Seule une affectation brouillon peut etre annulee.")
        return self._replace_status(StudentAssignmentStatus.CANCELLED)

    def close(self) -> "StudentAssignment":
        if self.status is not StudentAssignmentStatus.ACTIVE:
            raise ValueError("Seule une affectation active peut etre cloturee.")
        return self._replace_status(StudentAssignmentStatus.CLOSED)

    def _replace_status(self, status: StudentAssignmentStatus) -> "StudentAssignment":
        now = datetime.now().astimezone()
        return StudentAssignment(
            id=self.id,
            tenant_id=self.tenant_id,
            student_id=self.student_id,
            academic_year_id=self.academic_year_id,
            academic_class_id=self.academic_class_id,
            academic_option_id=self.academic_option_id,
            status=status,
            created_by=self.created_by,
            created_at=self.created_at,
            updated_at=now,
            closed_at=now if status in {
                StudentAssignmentStatus.CLOSED,
                StudentAssignmentStatus.CANCELLED,
            } else None,
        )
