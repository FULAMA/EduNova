from abc import ABC, abstractmethod
from uuid import UUID


class TotpAntiReplayRepository(ABC):
    """Interface for persistent TOTP anti-replay protection.

    Tracks the last accepted TOTP time interval per user to prevent
    code reuse across server restarts and multiple processes.
    """

    @abstractmethod
    def record_interval(
        self,
        user_id: UUID,
        interval_index: int,
    ) -> bool:
        """Atomically records a TOTP interval if it's newer than the last accepted.

        Args:
            user_id: The user identifier.
            interval_index: The TOTP time interval (typically time() // 30).

        Returns:
            True if the interval was recorded (first time or newer),
            False if the interval was already accepted (replay detected).
        """
        raise NotImplementedError

    @abstractmethod
    def get_last_interval(self, user_id: UUID) -> int | None:
        """Retrieves the last accepted TOTP interval for a user.

        Args:
            user_id: The user identifier.

        Returns:
            The last accepted interval index, or None if no interval recorded.
        """
        raise NotImplementedError
