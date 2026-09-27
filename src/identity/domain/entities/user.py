from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    role: str
    is_active: bool = True
    two_factor_enabled: bool = False
    two_factor_secret: str | None = None

    def __post_init__(self):
        if not self.email.strip():
            raise ValueError(
                "L email ne peut pas etre vide."
            )

        if not self.password_hash.strip():
            raise ValueError(
                "Le hash du mot de passe ne peut pas etre vide."
            )

        if not self.role.strip():
            raise ValueError(
                "Le role ne peut pas etre vide."
            )
