from dataclasses import dataclass


@dataclass(frozen=True)
class AgentProvider:
    name: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Provider name cannot be empty.")
