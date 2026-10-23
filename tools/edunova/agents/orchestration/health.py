from enum import Enum


class HealthStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    COOLDOWN = "COOLDOWN"


class HealthTracker:
    def __init__(self) -> None:
        self._statuses: dict[str, HealthStatus] = {}

    def status(self, provider_name: str) -> HealthStatus:
        return self._statuses.get(
            provider_name,
            HealthStatus.AVAILABLE,
        )

    def mark_available(self, provider_name: str) -> None:
        self._statuses[provider_name] = HealthStatus.AVAILABLE

    def mark_unavailable(self, provider_name: str) -> None:
        self._statuses[provider_name] = HealthStatus.UNAVAILABLE

    def mark_cooldown(self, provider_name: str) -> None:
        self._statuses[provider_name] = HealthStatus.COOLDOWN

    def is_available(self, provider_name: str) -> bool:
        return self.status(provider_name) == HealthStatus.AVAILABLE
