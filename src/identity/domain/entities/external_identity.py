from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ExternalIdentity:
    id: UUID
    provider: str
    subject: str
    user_id: UUID

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("Le fournisseur d identite est obligatoire.")
        if not self.subject:
            raise ValueError("Le sujet de l identite externe est obligatoire.")
