from tools.edunova.agents.orchestration.health import (
    HealthStatus,
    HealthTracker,
)


def test_new_provider_is_available() -> None:
    tracker = HealthTracker()

    assert tracker.status("gemini") == HealthStatus.AVAILABLE


def test_provider_can_be_marked_unavailable() -> None:
    tracker = HealthTracker()

    tracker.mark_unavailable("gemini")

    assert tracker.status("gemini") == HealthStatus.UNAVAILABLE


def test_provider_can_be_restored() -> None:
    tracker = HealthTracker()

    tracker.mark_unavailable("gemini")
    tracker.mark_available("gemini")

    assert tracker.status("gemini") == HealthStatus.AVAILABLE


def test_provider_can_enter_cooldown() -> None:
    tracker = HealthTracker()

    tracker.mark_cooldown("gemini")

    assert tracker.status("gemini") == HealthStatus.COOLDOWN


def test_unknown_provider_is_available_by_default() -> None:
    tracker = HealthTracker()

    assert tracker.status("unknown") == HealthStatus.AVAILABLE


def test_is_available_returns_false_for_unavailable_provider() -> None:
    tracker = HealthTracker()

    tracker.mark_unavailable("gemini")

    assert tracker.is_available("gemini") is False


def test_is_available_returns_false_during_cooldown() -> None:
    tracker = HealthTracker()

    tracker.mark_cooldown("gemini")

    assert tracker.is_available("gemini") is False


def test_is_available_returns_true_for_available_provider() -> None:
    tracker = HealthTracker()

    assert tracker.is_available("gemini") is True
