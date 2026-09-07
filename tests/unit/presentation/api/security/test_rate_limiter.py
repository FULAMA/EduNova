import pytest

from src.presentation.api.security.rate_limiter import RateLimiter


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_rate_limiter_allows_until_limit():
    limiter = RateLimiter(
        max_attempts=2,
        window_seconds=60,
        time_source=FakeClock(),
    )

    assert limiter.is_allowed("login:1.2.3.4") is True
    assert limiter.is_allowed("login:1.2.3.4") is True
    assert limiter.is_allowed("login:1.2.3.4") is False


def test_rate_limiter_isolates_keys():
    limiter = RateLimiter(
        max_attempts=1,
        window_seconds=60,
        time_source=FakeClock(),
    )

    assert limiter.is_allowed("login:1.2.3.4") is True
    assert limiter.is_allowed("login:5.6.7.8") is True


def test_rate_limiter_frees_slots_after_window():
    clock = FakeClock()

    limiter = RateLimiter(
        max_attempts=1,
        window_seconds=60,
        time_source=clock,
    )

    assert limiter.is_allowed("login:1.2.3.4") is True
    assert limiter.is_allowed("login:1.2.3.4") is False

    clock.advance(60)

    assert limiter.is_allowed("login:1.2.3.4") is True


def test_rate_limiter_reports_retry_after():
    clock = FakeClock()

    limiter = RateLimiter(
        max_attempts=1,
        window_seconds=60,
        time_source=clock,
    )

    limiter.is_allowed("login:1.2.3.4")

    clock.advance(10)

    assert limiter.retry_after_seconds("login:1.2.3.4") == 51


def test_rate_limiter_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        RateLimiter(max_attempts=0, window_seconds=60)

    with pytest.raises(ValueError):
        RateLimiter(max_attempts=1, window_seconds=0)
