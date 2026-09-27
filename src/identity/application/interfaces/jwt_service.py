from abc import ABC, abstractmethod
from uuid import UUID


class JwtService(ABC):

    @abstractmethod
    def create_access_token(
        self,
        user_id: UUID,
        role: str,
        tenant_id: UUID,
    ) -> str:
        pass

    @abstractmethod
    def create_refresh_token(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> str:
        pass

    @abstractmethod
    def create_two_factor_token(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        pass

    @abstractmethod
    def decode_refresh_token(self, token: str) -> dict:
        pass
