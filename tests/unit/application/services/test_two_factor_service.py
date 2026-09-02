import pyotp
import pytest

from src.application.services.two_factor_service import (
    TwoFactorService,
)


def test_generate_secret_returns_valid_totp_secret():
    service = TwoFactorService()

    secret = service.generate_secret()

    assert isinstance(secret, str)
    assert len(secret) >= 16
    assert pyotp.TOTP(secret).now()


def test_generate_provisioning_uri_contains_edunova():
    service = TwoFactorService()

    secret = service.generate_secret()

    uri = service.generate_provisioning_uri(
        email="admin@edunova.com",
        secret=secret,
    )

    assert uri.startswith("otpauth://totp/")
    assert "EduNova" in uri
    assert "admin%40edunova.com" in uri


def test_verify_valid_code_returns_true():
    service = TwoFactorService()

    secret = service.generate_secret()
    code = pyotp.TOTP(secret).now()

    assert service.verify_code(
        secret=secret,
        code=code,
    ) is True


def test_verify_invalid_code_returns_false():
    service = TwoFactorService()

    secret = service.generate_secret()

    assert service.verify_code(
        secret=secret,
        code="000000",
    ) is False


def test_verify_code_requires_six_digits():
    service = TwoFactorService()

    secret = service.generate_secret()

    with pytest.raises(ValueError):
        service.verify_code(
            secret=secret,
            code="12345",
        )


def test_verify_code_rejects_non_numeric_code():
    service = TwoFactorService()

    secret = service.generate_secret()

    with pytest.raises(ValueError):
        service.verify_code(
            secret=secret,
            code="ABC123",
        )


def test_empty_secret_is_rejected():
    service = TwoFactorService()

    with pytest.raises(ValueError):
        service.generate_provisioning_uri(
            email="admin@edunova.com",
            secret="",
        )
