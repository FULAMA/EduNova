import pyotp
import pytest

from src.identity.infrastructure.security.pyotp_two_factor_service import (
    PyOtpTwoFactorService,
)


def test_generate_secret_returns_valid_totp_secret():
    service = PyOtpTwoFactorService()

    secret = service.generate_secret()

    assert isinstance(secret, str)
    assert len(secret) >= 16
    assert pyotp.TOTP(secret).now()


def test_generate_provisioning_uri_contains_edunova():
    service = PyOtpTwoFactorService()

    secret = service.generate_secret()

    uri = service.generate_provisioning_uri(
        email="admin@edunova.com",
        secret=secret,
    )

    assert uri.startswith("otpauth://totp/")
    assert "EduNova" in uri
    assert "admin%40edunova.com" in uri


def test_verify_valid_code_returns_true():
    service = PyOtpTwoFactorService()

    secret = service.generate_secret()
    code = pyotp.TOTP(secret).now()

    assert service.verify_code(
        secret=secret,
        code=code,
    ) is True


def test_verify_invalid_code_returns_false():
    service = PyOtpTwoFactorService()

    secret = service.generate_secret()

    assert service.verify_code(
        secret=secret,
        code="000000",
    ) is False


def test_verify_code_requires_six_digits():
    service = PyOtpTwoFactorService()

    secret = service.generate_secret()

    with pytest.raises(ValueError):
        service.verify_code(
            secret=secret,
            code="12345",
        )


def test_verify_code_rejects_non_numeric_code():
    service = PyOtpTwoFactorService()

    secret = service.generate_secret()

    with pytest.raises(ValueError):
        service.verify_code(
            secret=secret,
            code="ABC123",
        )


def test_empty_secret_is_rejected():
    service = PyOtpTwoFactorService()

    with pytest.raises(ValueError):
        service.generate_provisioning_uri(
            email="admin@edunova.com",
            secret="",
        )


def test_generate_provisioning_uri_rejects_empty_email():
    service = PyOtpTwoFactorService()

    secret = service.generate_secret()

    with pytest.raises(ValueError, match="L email ne peut pas etre vide"):
        service.generate_provisioning_uri(
            email="",
            secret=secret,
        )


def test_verify_code_rejects_empty_secret():
    service = PyOtpTwoFactorService()

    with pytest.raises(
        ValueError,
        match="Le secret 2FA ne peut pas etre vide",
    ):
        service.verify_code(
            secret="",
            code="123456",
        )


