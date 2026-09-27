from .command_registry import CommandRegistry
from .result import CommandResult
from .runner import CommandRunner


class CommandService:
    def __init__(
        self,
        registry: CommandRegistry,
        runner: CommandRunner,
    ) -> None:
        self._registry = registry
        self._runner = runner

    def execute(self, name: str) -> CommandResult:
        command = self._registry.get(name)
        return self._runner.run(command)
