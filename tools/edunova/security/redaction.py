from __future__ import annotations

import re


_PRIVATE_KEY = re.compile(
    r"-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----",
    re.IGNORECASE | re.DOTALL,
)
_BEARER = re.compile(r"(\bBearer\s+)[A-Za-z0-9._~+/=-]+", re.IGNORECASE)
_AUTH_URL = re.compile(
    r"(https?://)([^\s/:@]+):([^\s/@]+)@",
    re.IGNORECASE,
)
_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|"
    r"password|passwd|secret|token|client[_-]?secret)"
    r"(\s*[:=]\s*)([\"']?)([^\"'\s,;]+)(?:\3)?"
)
_KNOWN_TOKEN = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9_]{8,}|"
    r"xox[baprs]-[A-Za-z0-9-]{8,}|AKIA[0-9A-Z]{16})\b"
)


def redact_text(value: str) -> str:
    """Redact common credentials from text intended for users or logs."""
    if not isinstance(value, str):
        value = str(value)

    redacted = _PRIVATE_KEY.sub("[REDACTED_PRIVATE_KEY]", value)
    redacted = _AUTH_URL.sub(r"\1[REDACTED]:[REDACTED]@", redacted)
    redacted = _BEARER.sub(r"\1[REDACTED]", redacted)
    redacted = _ASSIGNMENT.sub(r"\1\2[REDACTED]", redacted)
    return _KNOWN_TOKEN.sub("[REDACTED_TOKEN]", redacted)


def redact_exception(error: BaseException) -> str:
    """Return a safe exception description without exposing raw credentials."""
    return redact_text(str(error))
