from dataclasses import dataclass


@dataclass(frozen=True)
class VerifyLoginTwoFactorRequest:
    two_factor_token: str
    code: str
