import threading
import pytest

from src.identity.infrastructure.security.in_memory_rate_limiter import (
    InMemoryRateLimiter,
)


def test_rate_limiter_allows_under_limit():
    limiter = InMemoryRateLimiter()
    result = limiter.check_and_record("test:key", limit=3, window_seconds=60)
    assert result.allowed is True
    assert result.limit == 3
    assert result.remaining == 2
    assert result.retry_after == 0


def test_rate_limiter_blocks_over_limit():
    limiter = InMemoryRateLimiter()
    for _ in range(3):
        res = limiter.check_and_record("test:key", limit=3, window_seconds=60)
        assert res.allowed is True

    blocked = limiter.check_and_record("test:key", limit=3, window_seconds=60)
    assert blocked.allowed is False
    assert blocked.remaining == 0
    assert blocked.retry_after > 0


def test_rate_limiter_isolates_different_keys():
    limiter = InMemoryRateLimiter()
    for _ in range(3):
        limiter.check_and_record("user:alice", limit=3, window_seconds=60)

    # alice is blocked
    assert limiter.check_and_record("user:alice", limit=3, window_seconds=60).allowed is False
    # bob is allowed
    assert limiter.check_and_record("user:bob", limit=3, window_seconds=60).allowed is True


def test_rate_limiter_window_expiration():
    fake_time = 1000.0

    def time_provider():
        return fake_time

    limiter = InMemoryRateLimiter(time_provider=time_provider)

    for _ in range(3):
        limiter.check_and_record("key", limit=3, window_seconds=10)

    assert limiter.check_and_record("key", limit=3, window_seconds=10).allowed is False

    # Advance time beyond window
    fake_time += 11.0
    res = limiter.check_and_record("key", limit=3, window_seconds=10)
    assert res.allowed is True
    assert res.remaining == 2


def test_rate_limiter_reset():
    limiter = InMemoryRateLimiter()
    for _ in range(3):
        limiter.check_and_record("key", limit=3, window_seconds=60)

    assert limiter.check_and_record("key", limit=3, window_seconds=60).allowed is False

    limiter.reset("key")
    res = limiter.check_and_record("key", limit=3, window_seconds=60)
    assert res.allowed is True
    assert res.remaining == 2


def test_rate_limiter_is_limited_does_not_consume_quota():
    limiter = InMemoryRateLimiter()
    assert limiter.is_limited("key", limit=2, window_seconds=60) is False

    limiter.check_and_record("key", limit=2, window_seconds=60)
    assert limiter.is_limited("key", limit=2, window_seconds=60) is False

    limiter.check_and_record("key", limit=2, window_seconds=60)
    assert limiter.is_limited("key", limit=2, window_seconds=60) is True

    # is_limited does not add attempts
    assert limiter.is_limited("key", limit=2, window_seconds=60) is True


def test_rate_limiter_invalid_parameters():
    limiter = InMemoryRateLimiter()
    with pytest.raises(ValueError, match="seuil"):
        limiter.check_and_record("key", limit=0, window_seconds=60)

    with pytest.raises(ValueError, match="fenetre"):
        limiter.check_and_record("key", limit=5, window_seconds=0)


def test_rate_limiter_thread_safety_under_concurrency():
    limiter = InMemoryRateLimiter()
    limit = 50
    allowed_count = 0
    lock = threading.Lock()

    def worker():
        nonlocal allowed_count
        res = limiter.check_and_record("shared:key", limit=limit, window_seconds=60)
        if res.allowed:
            with lock:
                allowed_count += 1

    threads = [threading.Thread(target=worker) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Exactly 50 requests must have been allowed despite 100 simultaneous threads
    assert allowed_count == limit
