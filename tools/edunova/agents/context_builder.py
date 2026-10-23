from tools.edunova.agents.context import EngineeringContext


class ContextBuilder:
    def __init__(self, scanner) -> None:
        self._scanner = scanner

    def build(self) -> EngineeringContext:
        return self._scanner.scan()
