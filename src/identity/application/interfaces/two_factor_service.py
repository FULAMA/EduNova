from abc import ABC, abstractmethod


class TwoFactorService(ABC):

    @abstractmethod
    def generate_secret(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_provisioning_uri(
        self,
        email: str,
        secret: str,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify_code(
        self,
        secret: str,
        code: str,
    ) -> bool:
        raise NotImplementedError