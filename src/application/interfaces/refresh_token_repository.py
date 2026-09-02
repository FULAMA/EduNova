from abc import ABC, abstractmethod


class RefreshTokenRepository(ABC):

    @abstractmethod
    def revoke(self, jti: str) -> None:
        pass

    @abstractmethod
    def is_revoked(self, jti: str) -> bool:
        pass
