from abc import ABC, abstractmethod


class ConsumedTokenRepository(ABC):
    """Interface for managing single-use token consumption and anti-replay."""

    @abstractmethod
    def consume(self, jti: str) -> bool:
        """Atomically marks a token jti as consumed.

        Returns True if the token was successfully recorded (first time),
        or False if it was already consumed.
        """
        raise NotImplementedError

    @abstractmethod
    def is_consumed(self, jti: str) -> bool:
        """Checks whether a token jti has already been consumed."""
        raise NotImplementedError
