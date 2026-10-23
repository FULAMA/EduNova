from dataclasses import dataclass
from datetime import date
from enum import Enum
from uuid import UUID


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"


@dataclass(frozen=True)
class Attendance:
    id: UUID
    tenant_id: UUID
    student_id: UUID
    academic_class_id: UUID
    academic_year_id: UUID
    academic_period_id: UUID
    attendance_date: date
    status: AttendanceStatus
    justified: bool = False
    recorded_by: UUID | None = None
    version: int = 1

    def __post_init__(self):
        identifiers = (self.id, self.tenant_id, self.student_id,
                       self.academic_class_id, self.academic_year_id,
                       self.academic_period_id)
        if not all(isinstance(identifier, UUID) for identifier in identifiers):
            raise TypeError("Les identifiants du relevé doivent etre des UUID.")
        if self.recorded_by is not None and not isinstance(self.recorded_by, UUID):
            raise TypeError("L'identifiant de l'auteur doit etre un UUID.")
        if self.version <= 0:
            raise ValueError("La version du releve doit etre superieure a zero.")
        if not isinstance(self.attendance_date, date):
            raise TypeError("La date du relevé doit etre une date.")
        if not isinstance(self.status, AttendanceStatus):
            raise TypeError("Le statut de présence est invalide.")
        if self.status == AttendanceStatus.PRESENT and self.justified:
            raise ValueError(
                "Une présence ne peut pas être justifiée."
            )

    @property
    def is_absent(self) -> bool:
        return self.status == AttendanceStatus.ABSENT

    @property
    def is_late(self) -> bool:
        return self.status == AttendanceStatus.LATE

    def corrected(self, status: AttendanceStatus, justified: bool) -> "Attendance":
        return Attendance(
            id=self.id,
            tenant_id=self.tenant_id,
            student_id=self.student_id,
            academic_class_id=self.academic_class_id,
            academic_year_id=self.academic_year_id,
            academic_period_id=self.academic_period_id,
            attendance_date=self.attendance_date,
            status=status,
            justified=justified,
            recorded_by=self.recorded_by,
            version=self.version + 1,
        )
