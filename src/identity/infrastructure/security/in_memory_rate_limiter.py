import threading
import time
from collections import defaultdict
from typing import Callable, DefaultDict, List

from src.identity.application.interfaces.rate_limiter import (
    RateLimiter,
    RateLimitResult,
)


class InMemoryRateLimiter(RateLimiter):
    """Thread-safe sliding-window in-memory rate limiter using monotonic timestamps.

    Maintains per-key hit histories and automatically prunes expired timestamps.
    Note: In-memory state is local to the current process/worker.
    For multi-worker or distributed deployments, an implementation backed by a shared
    cache (e.g. Redis) conforming to RateLimiter should be substituted.
    """

    def __init__(
        self,
        time_provider: Callable[[], float] = time.monotonic,
    ) -> None:
        self._time_provider = time_provider
        self._lock = threading.Lock()
        self._hits: DefaultDict[str, List[float]] = defaultdict(list)

    def check_and_record(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> RateLimitResult:
        if limit <= 0:
            raise ValueError(
                "Le seuil de rate limiting doit etre superieur a zero."
            )
        if window_seconds <= 0:
            raise ValueError(
                "La fenetre de rate limiting doit etre superieure a zero."
            )

        now = self._time_provider()
        cutoff = now - window_seconds

        with self._lock:
            timestamps = [ts for ts in self._hits[key] if ts > cutoff]
            self._hits[key] = timestamps

            count = len(timestamps)
            if count >= limit:
                oldest_in_window = timestamps[0]
                retry_after = max(
                    1,
                    int(oldest_in_window + window_seconds - now + 0.999),
                )
                return RateLimitResult(
                    allowed=False,
                    limit=limit,
                    remaining=0,
                    retry_after=retry_after,
                )

            timestamps.append(now)
            remaining = limit - len(timestamps)
            return RateLimitResult(
                allowed=True,
                limit=limit,
                remaining=remaining,
                retry_after=0,
            )

    def is_limited(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        if limit <= 0 or window_seconds <= 0:
            return True

        now = self._time_provider()
        cutoff = now - window_seconds

        with self._lock:
            timestamps = [ts for ts in self._hits[key] if ts > cutoff]
            self._hits[key] = timestamps
            return len(timestamps) >= limit

    def reset(self, key: str) -> None:
        with self._lock:
            if key in self._hits:
                del self._hits[key]
