from dataclasses import dataclass
from datetime import date
from enum import Enum
from uuid import UUID


class AcademicYearStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class AcademicYear:
    id: UUID
    tenant_id: UUID
    label: str
    start_date: date
    end_date: date
    status: AcademicYearStatus = AcademicYearStatus.DRAFT

    def __post_init__(self) -> None:
        if not isinstance(self.id, UUID):
            raise TypeError("L'identifiant de l'annee doit etre un UUID.")
        if not isinstance(self.tenant_id, UUID):
            raise TypeError("Le tenant doit etre un UUID.")
        if not isinstance(self.label, str):
            raise TypeError("Le libelle doit etre une chaine.")
        if not isinstance(self.start_date, date) or not isinstance(self.end_date, date):
            raise TypeError("Les dates de l'annee doivent etre des dates.")
        if not isinstance(self.status, AcademicYearStatus):
            raise TypeError("Le statut de l'annee est invalide.")
        if len(self.label) != 9 or self.label[4] not in "-–":
            raise ValueError("Le libelle doit suivre le format YYYY-YYYY.")
        if (
            not self.label[:4].isdigit()
            or not self.label[5:].isdigit()
        ):
            raise ValueError("Le libelle doit suivre le format YYYY-YYYY.")
        if self.end_date <= self.start_date:
            raise ValueError("La date de fin doit etre posterieure a la date de debut.")

    def activate(self) -> "AcademicYear":
        if self.status is not AcademicYearStatus.DRAFT:
            raise ValueError("Seule une annee brouillon peut etre activee.")
        return AcademicYear(
            self.id, self.tenant_id, self.label, self.start_date,
            self.end_date, AcademicYearStatus.ACTIVE,
        )

    def close(self) -> "AcademicYear":
        if self.status is not AcademicYearStatus.ACTIVE:
            raise ValueError("Seule une annee active peut etre cloturee.")
        return AcademicYear(
            self.id, self.tenant_id, self.label, self.start_date,
            self.end_date, AcademicYearStatus.CLOSED,
        )
