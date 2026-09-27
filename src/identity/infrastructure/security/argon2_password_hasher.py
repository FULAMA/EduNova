from src.identity.application.interfaces.password_hasher import PasswordHasher
from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError, VerificationError


class Argon2PasswordHasher(PasswordHasher):

    def __init__(self):
        self._hasher = Argon2Hasher()

    def hash(self, password: str) -> str:
        if not password:
            raise ValueError(
                "Le mot de passe ne peut pas etre vide."
            )

        return self._hasher.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        if not password_hash:
            raise ValueError(
                "Le hash du mot de passe ne peut pas etre vide."
            )

        try:
            return self._hasher.verify(
                password_hash,
                password,
            )
        except (VerifyMismatchError, VerificationError):
            return False
