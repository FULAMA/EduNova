from src.identity.application.interfaces.two_factor_service import (
    TwoFactorService,
)
import pyotp


class PyOtpTwoFactorService(TwoFactorService):

    def generate_secret(self) -> str:
        return pyotp.random_base32()

    def generate_provisioning_uri(
        self,
        email: str,
        secret: str,
    ) -> str:
        if not email.strip():
            raise ValueError(
                "L email ne peut pas etre vide."
            )

        if not secret.strip():
            raise ValueError(
                "Le secret 2FA ne peut pas etre vide."
            )

        totp = pyotp.TOTP(secret)

        return totp.provisioning_uri(
            name=email,
            issuer_name="EduNova",
        )

    def verify_code(
        self,
        secret: str,
        code: str,
    ) -> bool:
        if not secret.strip():
            raise ValueError(
                "Le secret 2FA ne peut pas etre vide."
            )

        if not code.isdigit() or len(code) != 6:
            raise ValueError(
                "Le code 2FA doit contenir exactement 6 chiffres."
            )

        totp = pyotp.TOTP(secret)

        return totp.verify(code)
