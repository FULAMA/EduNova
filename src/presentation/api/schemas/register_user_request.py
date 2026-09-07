import re

from pydantic import BaseModel, Field, field_validator


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$"
)

MINIMUM_PASSWORD_LENGTH = 12

MAXIMUM_PASSWORD_LENGTH = 128


class RegisterUserRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(
        min_length=MINIMUM_PASSWORD_LENGTH,
        max_length=MAXIMUM_PASSWORD_LENGTH,
    )
    role: str | None = Field(default=None, min_length=1, max_length=32)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()

        if not EMAIL_PATTERN.match(normalized):
            raise ValueError("L adresse email est invalide.")

        return normalized

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(character.islower() for character in value):
            raise ValueError(
                "Le mot de passe doit contenir une minuscule."
            )

        if not any(character.isupper() for character in value):
            raise ValueError(
                "Le mot de passe doit contenir une majuscule."
            )

        if not any(character.isdigit() for character in value):
            raise ValueError(
                "Le mot de passe doit contenir un chiffre."
            )

        return value
