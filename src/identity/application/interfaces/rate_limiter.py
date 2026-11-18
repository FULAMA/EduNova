from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after: int  # in seconds


class RateLimiter(ABC):
    """Port for rate-limiting operations (token bucket / sliding window)."""

    @abstractmethod
    def check_and_record(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> RateLimitResult:
        """Check if request under key is allowed within window, and record it.

        Args:
            key: Unique bucket identifier (e.g. "login:ip:1.2.3.4").
            limit: Maximum allowed attempts in the window.
            window_seconds: Duration of the sliding window in seconds.

        Returns:
            RateLimitResult indicating if allowed, remaining attempts, and retry_after seconds.
        """
        pass

    @abstractmethod
    def is_limited(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        """Check if key has reached or exceeded limit without recording a new attempt."""
        pass

    @abstractmethod
    def reset(self, key: str) -> None:
        """Reset the attempt counter for a specific key (e.g. after successful authentication)."""
        pass
