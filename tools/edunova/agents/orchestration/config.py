from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    enabled: bool = True
    priority: int = 1
    model: str = ""
    timeout: int = 60

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Provider name cannot be empty.")

        if self.priority <= 0:
            raise ValueError("Provider priority must be greater than zero.")

        if self.timeout <= 0:
            raise ValueError("Provider timeout must be greater than zero.")
