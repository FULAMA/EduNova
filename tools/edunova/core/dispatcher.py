from .command_service import CommandService
from .result import CommandResult


class CommandDispatcher:
    def __init__(self, service: CommandService) -> None:
        self._service = service

    def dispatch(self, name: str) -> CommandResult:
        return self._service.execute(name)
