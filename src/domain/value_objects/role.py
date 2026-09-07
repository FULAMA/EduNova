from typing import Final


ADMIN: Final = "ADMIN"
TEACHER: Final = "TEACHER"
STUDENT: Final = "STUDENT"

ALLOWED_ROLES: Final = frozenset({ADMIN, TEACHER, STUDENT})

# Roles qu un visiteur anonyme peut demander lors de l inscription.
SELF_SERVICE_ROLES: Final = frozenset({STUDENT})


def normalize_role(role: str) -> str:
    normalized = role.strip().upper()

    if normalized not in ALLOWED_ROLES:
        raise ValueError("Le role demande est invalide.")

    return normalized
