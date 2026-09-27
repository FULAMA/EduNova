from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.student_academic_record import StudentAcademicRecord


class StudentAcademicRecordRepository(ABC):

    @abstractmethod
    def save(self, record: StudentAcademicRecord) -> None:
        """Enregistre ou remplace un dossier académique."""
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
