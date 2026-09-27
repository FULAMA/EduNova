from tools.edunova.commands.quality import QualityCommand
from tools.edunova.core.result import Status


def test_quality_command_has_correct_name() -> None:
    command = QualityCommand()

    assert command.name == "quality"


def test_quality_command_returns_command_result() -> None:
    command = QualityCommand()

    result = command.execute()

    assert result.command == "quality"
    assert result.status in {
        Status.SAFE,
        Status.WARN,
        Status.REVIEW,
        Status.FAIL,
    }
