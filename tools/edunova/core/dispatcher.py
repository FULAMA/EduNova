from collections.abc import Sequence

from .command_service import CommandService
from .result import CommandResult


class CommandDispatcher:
    def __init__(self, service: CommandService) -> None:
        self._service = service

    def dispatch(
        self,
        name: str,
        args: Sequence[str] = (),
    ) -> CommandResult:
        return self._service.execute(name, args)
