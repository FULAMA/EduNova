from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GoogleIdentity:
    subject: str
    email: str
    email_verified: bool


class GoogleIdentityVerifier(ABC):
    @abstractmethod
    def verify(self, id_token: str) -> GoogleIdentity:
        raise NotImplementedError
