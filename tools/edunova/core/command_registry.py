from tools.edunova.core.command import Command


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        if command.name in self._commands:
            raise ValueError(
                f"Command already registered: {command.name}"
            )

        self._commands[command.name] = command

    def get(self, name: str) -> Command:
        if name not in self._commands:
            raise KeyError(f"Unknown command: {name}")

        return self._commands[name]

    def has(self, name: str) -> bool:
        return name in self._commands

    def names(self) -> tuple[str, ...]:
        return tuple(self._commands)
