"""
SQLite Enrollment Repository - Infrastructure Layer

SQLite implementation of the EnrollmentRepository interface.
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from src.academic.application.interfaces.enrollment_repository import EnrollmentRepository
from src.academic.domain.entities.enrollment import Enrollment, EnrollmentStatus
from src.shared.infrastructure.repositories.sqlite_base_repository import SQLiteBaseRepository


class SQLiteEnrollmentRepository(
    SQLiteBaseRepository[Enrollment],
    EnrollmentRepository,
):
    """
    SQLite implementation for EnrollmentRepository.
    
    This repository handles persistence of Enrollment entities to SQLite database.
    """

    def __init__(self, database_path: str) -> None:
        super().__init__(database_path, "enrollments")

    def save(self, enrollment: Enrollment) -> Enrollment:
        """Save an enrollment to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if enrollment already exists
            cursor.execute(
                """
                SELECT id FROM enrollments 
                WHERE id = ? AND tenant_id = ?
                """,
                (str(enrollment.id), str(enrollment.tenant_id)),
            )
            
            if cursor.fetchone():
                # Update existing enrollment
                cursor.execute(
                    """
                    UPDATE enrollments SET
                        student_id = ?,
                        academic_year_id = ?,
                        academic_class_id = ?,
                        enrollment_date = ?,
                        end_date = ?,
                        status = ?,
                        previous_establishment = ?,
                        previous_class = ?,
                        transfer_reason = ?
                    WHERE id = ? AND tenant_id = ?
                    """,
                    (
                        str(enrollment.student_id),
                        str(enrollment.academic_year_id),
                        str(enrollment.academic_class_id),
                        enrollment.enrollment_date.isoformat(),
                        enrollment.end_date.isoformat() if enrollment.end_date else None,
                        enrollment.status.value,
                        enrollment.previous_establishment,
                        enrollment.previous_class,
                        enrollment.transfer_reason,
                        str(enrollment.id),
                        str(enrollment.tenant_id),
                    ),
                )
            else:
                # Insert new enrollment
                cursor.execute(
                    """
                    INSERT INTO enrollments (
                        id, tenant_id, student_id, academic_year_id,
                        academic_class_id, enrollment_date, end_date,
                        status, previous_establishment, previous_class, transfer_reason
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(enrollment.id),
                        str(enrollment.tenant_id),
                        str(enrollment.student_id),
                        str(enrollment.academic_year_id),
                        str(enrollment.academic_class_id),
                        enrollment.enrollment_date.isoformat(),
                        enrollment.end_date.isoformat() if enrollment.end_date else None,
                        enrollment.status.value,
                        enrollment.previous_establishment,
                        enrollment.previous_class,
                        enrollment.transfer_reason,
                    ),
                )
            
            conn.commit()
            return enrollment

    def find_by_id(self, enrollment_id: UUID) -> Optional[Enrollment]:
        """Find an enrollment by its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM enrollments 
                WHERE id = ?
                """,
                (str(enrollment_id),),
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_entity(row)

    def find_by_student(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> List[Enrollment]:
        """Find all enrollments for a specific student."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM enrollments 
                WHERE student_id = ? AND tenant_id = ?
                ORDER BY enrollment_date DESC
                """,
                (str(student_id), str(tenant_id)),
            )
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def find_by_class(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
        academic_year_id: Optional[UUID] = None,
    ) -> List[Enrollment]:
        """Find all enrollments for a specific class."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if academic_year_id:
                cursor.execute(
                    """
                    SELECT * FROM enrollments 
                    WHERE academic_class_id = ? AND tenant_id = ? 
                    AND academic_year_id = ?
                    ORDER BY enrollment_date DESC
                    """,
                    (str(academic_class_id), str(tenant_id), str(academic_year_id)),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM enrollments 
                    WHERE academic_class_id = ? AND tenant_id = ?
                    ORDER BY enrollment_date DESC
                    """,
                    (str(academic_class_id), str(tenant_id)),
                )
            
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def find_by_academic_year(
        self,
        academic_year_id: UUID,
        tenant_id: UUID,
    ) -> List[Enrollment]:
        """Find all enrollments for a specific academic year."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM enrollments 
                WHERE academic_year_id = ? AND tenant_id = ?
                ORDER BY enrollment_date DESC
                """,
                (str(academic_year_id), str(tenant_id)),
            )
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def find_active_by_student(
        self,
        student_id: UUID,
        tenant_id: UUID,
        academic_year_id: Optional[UUID] = None,
    ) -> Optional[Enrollment]:
        """Find the currently active enrollment for a student."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if academic_year_id:
                cursor.execute(
                    """
                    SELECT * FROM enrollments 
                    WHERE student_id = ? AND tenant_id = ?
                    AND academic_year_id = ? AND status = ?
                    ORDER BY enrollment_date DESC
                    LIMIT 1
                    """,
                    (
                        str(student_id),
                        str(tenant_id),
                        str(academic_year_id),
                        EnrollmentStatus.ACTIVE.value,
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM enrollments 
                    WHERE student_id = ? AND tenant_id = ?
                    AND status = ?
                    ORDER BY enrollment_date DESC
                    LIMIT 1
                    """,
                    (
                        str(student_id),
                        str(tenant_id),
                        EnrollmentStatus.ACTIVE.value,
                    ),
                )
            
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None

    def find_active_by_class(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
        academic_year_id: Optional[UUID] = None,
    ) -> List[Enrollment]:
        """Find all active enrollments for a class."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if academic_year_id:
                cursor.execute(
                    """
                    SELECT * FROM enrollments 
                    WHERE academic_class_id = ? AND tenant_id = ?
                    AND academic_year_id = ? AND status = ?
                    """,
                    (
                        str(academic_class_id),
                        str(tenant_id),
                        str(academic_year_id),
                        EnrollmentStatus.ACTIVE.value,
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM enrollments 
                    WHERE academic_class_id = ? AND tenant_id = ?
                    AND status = ?
                    """,
                    (
                        str(academic_class_id),
                        str(tenant_id),
                        EnrollmentStatus.ACTIVE.value,
                    ),
                )
            
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def get_students_in_class(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
        academic_year_id: Optional[UUID] = None,
    ) -> List[UUID]:
        """Get list of student IDs enrolled in a class."""
        enrollments = self.find_by_class(
            academic_class_id, tenant_id, academic_year_id
        )
        return [e.student_id for e in enrollments]

    def count_by_class(
        self,
        academic_class_id: UUID,
        tenant_id: UUID,
        academic_year_id: Optional[UUID] = None,
    ) -> int:
        """Count the number of students enrolled in a class."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if academic_year_id:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM enrollments 
                    WHERE academic_class_id = ? AND tenant_id = ?
                    AND academic_year_id = ?
                    """,
                    (str(academic_class_id), str(tenant_id), str(academic_year_id)),
                )
            else:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM enrollments 
                    WHERE academic_class_id = ? AND tenant_id = ?
                    """,
                    (str(academic_class_id), str(tenant_id)),
                )
            
            return cursor.fetchone()[0]

    def has_active_enrollment(
        self,
        student_id: UUID,
        academic_year_id: UUID,
        tenant_id: UUID,
    ) -> bool:
        """Check if a student has an active enrollment for a given academic year."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM enrollments 
                WHERE student_id = ? AND tenant_id = ?
                AND academic_year_id = ? AND status = ?
                """,
                (
                    str(student_id),
                    str(tenant_id),
                    str(academic_year_id),
                    EnrollmentStatus.ACTIVE.value,
                ),
            )
            return cursor.fetchone()[0] > 0

    def delete(self, enrollment_id: UUID, tenant_id: UUID) -> bool:
        """Delete an enrollment from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM enrollments 
                WHERE id = ? AND tenant_id = ?
                """,
                (str(enrollment_id), str(tenant_id)),
            )
            conn.commit()
            return cursor.rowcount > 0

    def _row_to_entity(self, row: tuple) -> Enrollment:
        """Convert a database row to an Enrollment entity."""
        return Enrollment(
            id=UUID(row[0]),
            tenant_id=UUID(row[1]),
            student_id=UUID(row[2]),
            academic_year_id=UUID(row[3]),
            academic_class_id=UUID(row[4]),
            enrollment_date=date.fromisoformat(row[5]),
            end_date=date.fromisoformat(row[6]) if row[6] else None,
            status=EnrollmentStatus(row[7]),
            previous_establishment=row[8],
            previous_class=row[9],
            transfer_reason=row[10],
        )
