from abc import ABC, abstractmethod

from .result import CommandResult


class Command(ABC):
    name: str

    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command."""
        raise NotImplementedError
