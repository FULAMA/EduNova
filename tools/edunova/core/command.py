from abc import ABC, abstractmethod
from collections.abc import Sequence

from .result import CommandResult


class Command(ABC):
    name: str

    def bind(self, args: Sequence[str]) -> "Command":
        return self

    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command."""
        raise NotImplementedError
