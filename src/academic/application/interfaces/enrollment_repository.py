"""
Enrollment Repository Interface - Application Layer

Defines the contract for persistence operations on Enrollment entities.
This follows the repository pattern to abstract data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.academic.domain.entities.enrollment import Enrollment


class EnrollmentRepository(ABC):
    """
    Repository interface for Enrollment entities.
    
    Provides methods to:
    - Create, read, update enrollments
    - Find enrollments by various criteria
    - Manage student transfers (D12)
    """

    @abstractmethod
    def save(self, enrollment: Enrollment) -> Enrollment:
        """Save an enrollment to the repository."""
        pass

    @abstractmethod
    def find_by_id(self, enrollment_id: UUID) -> Optional[Enrollment]:
        """Find an enrollment by its ID."""
        pass

    @abstractmethod
    def find_by_student(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> List[Enrollment]:
        """Find all enrollments for a specific student."""
        pass

    @abstractmethod
    def find_by_class(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
        academic_year_id: Optional[UUID] = None,
    ) -> List[Enrollment]:
        """Find all enrollments for a specific class."""
        pass

    @abstractmethod
    def find_by_academic_year(
        self,
        academic_year_id: UUID,
        tenant_id: UUID,
    ) -> List[Enrollment]:
        """Find all enrollments for a specific academic year."""
        pass

    @abstractmethod
    def find_active_by_student(
        self,
        student_id: UUID,
        tenant_id: UUID,
        academic_year_id: Optional[UUID] = None,
    ) -> Optional[Enrollment]:
        """
        Find the currently active enrollment for a student.
        
        Returns None if no active enrollment exists.
        """
        pass

    @abstractmethod
    def find_active_by_class(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
        academic_year_id: Optional[UUID] = None,
    ) -> List[Enrollment]:
        """Find all active enrollments for a class."""
        pass

    @abstractmethod
    def get_students_in_class(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
        academic_year_id: Optional[UUID] = None,
    ) -> List[UUID]:
        """Get list of student IDs enrolled in a class."""
        pass

    @abstractmethod
    def count_by_class(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
        academic_year_id: Optional[UUID] = None,
    ) -> int:
        """Count the number of students enrolled in a class."""
        pass

    @abstractmethod
    def has_active_enrollment(
        self,
        student_id: UUID,
        academic_year_id: UUID,
        tenant_id: UUID,
    ) -> bool:
        """Check if a student has an active enrollment for a given academic year."""
        pass

    @abstractmethod
    def delete(self, enrollment_id: UUID, tenant_id: UUID) -> bool:
        """Delete an enrollment from the repository."""
        pass
