from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SchoolProfile:
    tenant_id: UUID
    legal_name: str
    display_name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    logo_url: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("legal_name", "display_name"):
            value = getattr(self, field_name)
            if not value or not value.strip():
                raise ValueError(f"{field_name} ne peut pas être vide.")
        for field_name in ("address", "phone", "email", "website", "logo_url"):
            value = getattr(self, field_name)
            if value is not None and not value.strip():
                object.__setattr__(self, field_name, None)
        if self.email is not None and ("@" not in self.email or self.email.startswith("@") or self.email.endswith("@")):
            raise ValueError("Adresse e-mail invalide.")
