from tools.edunova.agents.orchestration.quota import (
    QuotaStatus,
    QuotaTracker,
)


def test_unknown_provider_is_available_by_default() -> None:
    tracker = QuotaTracker()

    assert tracker.status("gemini") == QuotaStatus.AVAILABLE
    assert tracker.is_available("gemini")


def test_provider_can_be_marked_exhausted() -> None:
    tracker = QuotaTracker()

    tracker.mark_exhausted("gemini")

    assert tracker.status("gemini") == QuotaStatus.EXHAUSTED
    assert not tracker.is_available("gemini")


def test_exhausted_provider_does_not_affect_another_provider() -> None:
    tracker = QuotaTracker()

    tracker.mark_exhausted("gemini")

    assert tracker.status("openrouter") == QuotaStatus.AVAILABLE
    assert tracker.is_available("openrouter")


def test_provider_can_be_reset() -> None:
    tracker = QuotaTracker()

    tracker.mark_exhausted("gemini")
    tracker.reset("gemini")

    assert tracker.status("gemini") == QuotaStatus.AVAILABLE
    assert tracker.is_available("gemini")


def test_multiple_providers_can_have_independent_quota_states() -> None:
    tracker = QuotaTracker()

    tracker.mark_exhausted("gemini")
    tracker.mark_exhausted("openrouter")

    assert tracker.status("gemini") == QuotaStatus.EXHAUSTED
    assert tracker.status("openrouter") == QuotaStatus.EXHAUSTED
    assert tracker.status("local") == QuotaStatus.AVAILABLE


def test_empty_provider_name_is_rejected() -> None:
    tracker = QuotaTracker()

    try:
        tracker.mark_exhausted("")
    except ValueError as exc:
        assert "provider" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")
