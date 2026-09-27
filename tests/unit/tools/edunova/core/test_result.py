from tools.edunova.core.result import CommandResult, Status


def test_command_result_is_successful_when_status_is_safe():
    result = CommandResult(
        command="test",
        status=Status.SAFE,
        message="Tests passed.",
    )

    assert result.succeeded is True


def test_command_result_is_not_successful_when_status_is_fail():
    result = CommandResult(
        command="test",
        status=Status.FAIL,
        message="Tests failed.",
        exit_code=1,
    )

    assert result.succeeded is False


def test_command_result_is_immutable():
    result = CommandResult(
        command="ruff",
        status=Status.SAFE,
        message="No errors.",
    )

    try:
        result.status = Status.FAIL
    except AttributeError:
        pass
    else:
        raise AssertionError("CommandResult should be immutable.")

def test_command_result_safe_uses_zero_exit_code() -> None:
    result = CommandResult(
        command="test",
        status=Status.SAFE,
        message="Tests passed.",
    )

    assert result.exit_code == 0


def test_command_result_warn_uses_zero_exit_code() -> None:
    result = CommandResult(
        command="quality",
        status=Status.WARN,
        message="Warnings detected.",
    )

    assert result.exit_code == 0


def test_command_result_review_uses_zero_exit_code() -> None:
    result = CommandResult(
        command="security",
        status=Status.REVIEW,
        message="Manual review required.",
    )

    assert result.exit_code == 0

def test_command_result_fail_uses_non_zero_exit_code() -> None:
    result = CommandResult(
        command="tests",
        status=Status.FAIL,
        message="Tests failed.",
        exit_code=1,
    )

    assert result.exit_code != 0
    assert result.succeeded is False

