import pytest

from tools.edunova.security import redact_exception, redact_text


@pytest.mark.parametrize(
    ("value", "secret"),
    [
        ("Authorization: Bearer abc.def.ghi", "abc.def.ghi"),
        ("api_key=abc123", "abc123"),
        ("password: p@ssword", "p@ssword"),
        ("https://user:pass123@example.test/path", "pass123"),
        ("output TOKEN=stdout-secret", "stdout-secret"),
        ("stderr: secret=stderr-secret", "stderr-secret"),
        ("provider returned sk-123456789", "sk-123456789"),
    ],
)
def test_redact_text_removes_common_secrets(value: str, secret: str) -> None:
    redacted = redact_text(value)

    assert secret not in redacted
    assert "[REDACTED" in redacted


def test_redact_text_removes_private_key_block() -> None:
    value = "-----BEGIN PRIVATE KEY-----\nsecret-material\n-----END PRIVATE KEY-----"

    assert "secret-material" not in redact_text(value)
    assert "[REDACTED_PRIVATE_KEY]" in redact_text(value)


def test_redact_text_preserves_non_sensitive_context() -> None:
    value = "pytest failed in tests/unit/test_cli.py"

    assert redact_text(value) == value


def test_redact_exception_keeps_type_but_not_secret() -> None:
    error = RuntimeError("api_key=do-not-print")

    message = redact_exception(error)

    assert "do-not-print" not in message
