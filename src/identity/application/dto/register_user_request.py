from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserRequest:
    email: str
    password: str
    role: str
