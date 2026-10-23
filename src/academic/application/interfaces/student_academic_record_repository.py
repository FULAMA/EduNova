from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.student_academic_record import StudentAcademicRecord


class StudentAcademicRecordRepository(ABC):

    def list_period_ids_by_student(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> tuple[UUID, ...]:
        """List periods with records for a student inside one tenant."""
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        record: StudentAcademicRecord,
        *,
        expected_version: int | None = None,
        operation: str = "SAVE",
        actor_id: UUID | None = None,
        reason: str | None = None,
    ) -> None:
        """Insert a new record, or update one using its expected version."""
        raise NotImplementedError

    @abstractmethod
    def find_by_student(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> StudentAcademicRecord | None:
        """Retourne le dossier académique d'un étudiant dans un tenant."""
        raise NotImplementedError

    @abstractmethod
    def find_by_student_and_period(
        self,
        student_id: UUID,
        academic_period_id: UUID,
        tenant_id: UUID,
    ) -> StudentAcademicRecord | None:
        """Retourne le dossier d'un étudiant pour une période dans un tenant."""
        raise NotImplementedError

    def list_history(
        self,
        student_id: UUID,
        academic_period_id: UUID,
        tenant_id: UUID,
    ) -> tuple[dict, ...]:
        """Return tenant-scoped immutable history entries."""
        raise NotImplementedError
