from abc import ABC, abstractmethod
from datetime import datetime


class GoogleNonceRepository(ABC):
    @abstractmethod
    def save(self, nonce_hash: str, expires_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    def consume(self, nonce_hash: str, now: datetime) -> bool:
        """Atomically consume an unexpired nonce exactly once."""
        raise NotImplementedError
