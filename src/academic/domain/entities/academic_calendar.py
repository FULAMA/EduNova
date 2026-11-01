from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AcademicCalendar:
    """A tenant-owned calendar that defines one independent period timeline."""

    id: UUID
    tenant_id: UUID
    name: str
    description: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.id, UUID):
            raise TypeError("L'identifiant du calendrier doit etre un UUID.")
        if not isinstance(self.tenant_id, UUID):
            raise TypeError("Le tenant du calendrier doit etre un UUID.")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Le nom du calendrier ne peut pas etre vide.")
        if self.description is not None and not isinstance(self.description, str):
            raise TypeError("La description du calendrier doit etre une chaine.")
        if not isinstance(self.is_active, bool):
            raise TypeError("Le statut du calendrier doit etre booleen.")
