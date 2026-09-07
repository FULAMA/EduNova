import threading
import time
from collections import deque


class RateLimiter:
    """Limiteur de debit en memoire, par cle et par fenetre glissante."""

    def __init__(
        self,
        max_attempts: int,
        window_seconds: int,
        time_source=time.monotonic,
    ):
        if max_attempts <= 0:
            raise ValueError(
                "Le nombre de tentatives doit etre positif."
            )

        if window_seconds <= 0:
            raise ValueError(
                "La fenetre doit etre positive."
            )

        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._time_source = time_source
        self._attempts: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    @property
    def max_attempts(self) -> int:
        return self._max_attempts

    @property
    def window_seconds(self) -> int:
        return self._window_seconds

    def is_allowed(self, key: str) -> bool:
        now = self._time_source()

        with self._lock:
            attempts = self._attempts.setdefault(key, deque())

            while attempts and now - attempts[0] >= self._window_seconds:
                attempts.popleft()

            if len(attempts) >= self._max_attempts:
                return False

            attempts.append(now)

            return True

    def retry_after_seconds(self, key: str) -> int:
        now = self._time_source()

        with self._lock:
            attempts = self._attempts.get(key)

            if not attempts:
                return 0

            remaining = self._window_seconds - (now - attempts[0])

            return max(1, int(remaining) + 1)

    def reset(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._attempts.clear()
            else:
                self._attempts.pop(key, None)
