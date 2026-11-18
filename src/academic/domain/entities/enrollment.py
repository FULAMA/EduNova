"""
Enrollment Entity - Domain Layer

Represents a student's enrollment in a specific academic class for a given academic year.
This entity is critical for implementing D12 (student transfers with history and provenance).
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from uuid import UUID


class EnrollmentStatus(str, Enum):
    """Status of a student's enrollment."""
    ACTIVE = "ACTIVE"
    TRANSFERRED = "TRANSFERRED"
    GRADUATED = "GRADUATED"
    WITHDRAWN = "WITHDRAWN"


@dataclass(frozen=True)
class Enrollment:
    """
    Represents a student's enrollment in an academic class for a specific academic year.
    
    This entity is the source of truth for:
    - Which students are in which classes
    - Student transfer history (D12)
    - Provenance information for transferred students
    - Enrollment dates and status
    
    Invariants:
    - A student can have multiple enrollments (for different academic years)
    - A student can have only ONE ACTIVE enrollment per academic year
    - TRANSFERRED enrollments must have provenance information
    - end_date must be >= enrollment_date
    """
    id: UUID
    tenant_id: UUID
    student_id: UUID
    academic_year_id: UUID
    academic_class_id: UUID
    enrollment_date: date
    end_date: date | None = None
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    previous_establishment: str | None = None
    previous_class: str | None = None
    transfer_reason: str | None = None

    def __post_init__(self) -> None:
        """Validate invariants."""
        # Type validations
        if not isinstance(self.id, UUID):
            raise TypeError("L'identifiant de l'inscription doit etre un UUID.")
        
        if not isinstance(self.tenant_id, UUID):
            raise TypeError("Le tenant doit etre un UUID.")
        
        if not isinstance(self.student_id, UUID):
            raise TypeError("L'identifiant de l'eleve doit etre un UUID.")
        
        if not isinstance(self.academic_year_id, UUID):
            raise TypeError("L'identifiant de l'annee scolaire doit etre un UUID.")
        
        if not isinstance(self.academic_class_id, UUID):
            raise TypeError("L'identifiant de la classe doit etre un UUID.")
        
        if not isinstance(self.enrollment_date, date):
            raise TypeError("La date d'inscription doit etre une date.")
        
        if not isinstance(self.status, EnrollmentStatus):
            raise TypeError("Le statut de l'inscription est invalide.")

        # Business rule validations
        if self.end_date is not None:
            if not isinstance(self.end_date, date):
                raise TypeError("La date de fin doit etre une date.")
            
            if self.end_date < self.enrollment_date:
                raise ValueError(
                    "La date de fin doit etre posterieure ou egale a la date d'inscription."
                )

        # D12: Provenance is required for TRANSFERRED enrollments
        if self.status == EnrollmentStatus.TRANSFERRED:
            if not self.previous_establishment:
                raise ValueError(
                    "La provenance de l'etablissement precedent est obligatoire "
                    "pour un transfert (D12)."
                )

    @property
    def is_active(self) -> bool:
        """Check if this enrollment is currently active."""
        return self.status == EnrollmentStatus.ACTIVE

    @property
    def has_ended(self) -> bool:
        """Check if this enrollment has ended."""
        return self.end_date is not None

    def transfer(
        self,
        new_class_id: UUID,
        end_date: date | None = None,
        new_establishment: str | None = None,
        reason: str | None = None,
    ) -> "Enrollment":
        """
        Create a new enrollment for a student transfer.
        
        This implements D12: Student transfers must maintain history and provenance.
        
        Args:
            new_class_id: The new class the student is transferring to
            end_date: The end date of this enrollment (defaults to today)
            new_establishment: The new establishment (if transferring to another school)
            reason: Reason for the transfer
            
        Returns:
            A new Enrollment entity representing the transfer
        """
        if self.status != EnrollmentStatus.ACTIVE:
            raise ValueError(
                "Seules les inscriptions actives peuvent etre transferees."
            )
        
        # Create new enrollment in the new class
        return Enrollment(
            id=UUID(),  # New UUID for the new enrollment
            tenant_id=self.tenant_id,
            student_id=self.student_id,
            academic_year_id=self.academic_year_id,
            academic_class_id=new_class_id,
            enrollment_date=end_date if end_date else self.enrollment_date,
            end_date=None,  # New enrollment has no end date yet
            status=EnrollmentStatus.ACTIVE,
            previous_establishment=new_establishment or self.previous_establishment,
            previous_class=str(self.academic_class_id),  # Store previous class as string
            transfer_reason=reason,
        )

    def withdraw(
        self,
        end_date: date | None = None,
        reason: str | None = None,
    ) -> "Enrollment":
        """
        Withdraw a student from their enrollment.
        
        Args:
            end_date: The effective withdrawal date
            reason: Reason for withdrawal
            
        Returns:
            A new Enrollment entity with WITHDRAWN status
        """
        if self.status != EnrollmentStatus.ACTIVE:
            raise ValueError(
                "Seules les inscriptions actives peuvent etre retirees."
            )
        
        return Enrollment(
            id=self.id,
            tenant_id=self.tenant_id,
            student_id=self.student_id,
            academic_year_id=self.academic_year_id,
            academic_class_id=self.academic_class_id,
            enrollment_date=self.enrollment_date,
            end_date=end_date if end_date else date.today(),
            status=EnrollmentStatus.WITHDRAWN,
            previous_establishment=self.previous_establishment,
            previous_class=self.previous_class,
            transfer_reason=reason,
        )

    def graduate(
        self,
        end_date: date | None = None,
    ) -> "Enrollment":
        """
        Mark a student as graduated from their enrollment.
        
        Args:
            end_date: The graduation date
            
        Returns:
            A new Enrollment entity with GRADUATED status
        """
        if self.status != EnrollmentStatus.ACTIVE:
            raise ValueError(
                "Seules les inscriptions actives peuvent etre marquees comme diplomees."
            )
        
        return Enrollment(
            id=self.id,
            tenant_id=self.tenant_id,
            student_id=self.student_id,
            academic_year_id=self.academic_year_id,
            academic_class_id=self.academic_class_id,
            enrollment_date=self.enrollment_date,
            end_date=end_date if end_date else date.today(),
            status=EnrollmentStatus.GRADUATED,
            previous_establishment=self.previous_establishment,
            previous_class=self.previous_class,
            transfer_reason=self.transfer_reason,
        )
