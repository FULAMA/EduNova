from enum import Enum


class QuotaStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    EXHAUSTED = "EXHAUSTED"


class QuotaTracker:
    def __init__(self) -> None:
        self._statuses: dict[str, QuotaStatus] = {}

    def status(self, provider_name: str) -> QuotaStatus:
        self._validate_provider_name(provider_name)
        return self._statuses.get(
            provider_name,
            QuotaStatus.AVAILABLE,
        )

    def mark_exhausted(self, provider_name: str) -> None:
        self._validate_provider_name(provider_name)
        self._statuses[provider_name] = QuotaStatus.EXHAUSTED

    def reset(self, provider_name: str) -> None:
        self._validate_provider_name(provider_name)
        self._statuses[provider_name] = QuotaStatus.AVAILABLE

    def is_available(self, provider_name: str) -> bool:
        return self.status(provider_name) == QuotaStatus.AVAILABLE

    @staticmethod
    def _validate_provider_name(provider_name: str) -> None:
        if not provider_name.strip():
            raise ValueError("Provider name cannot be empty.")
