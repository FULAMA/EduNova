import pytest

from src.infrastructure.security.google_identity_verifier import GoogleIdTokenVerifier


def test_google_verifier_requires_client_id():
    with pytest.raises(ValueError, match="Google auth non configuree"):
        GoogleIdTokenVerifier(None).verify("google-id-token")


def test_google_verifier_requires_verified_google_claims(monkeypatch):
    def fake_verify(token, request, audience):
        assert token == "google-id-token"
        assert audience == "google-client-id"
        return {
            "iss": "https://accounts.google.com",
            "sub": "google-subject",
            "email": "user@example.com",
            "email_verified": False,
        }

    monkeypatch.setattr(
        "src.infrastructure.security.google_identity_verifier.id_token.verify_oauth2_token",
        fake_verify,
    )

    identity = GoogleIdTokenVerifier("google-client-id").verify("google-id-token")

    assert identity.email == "user@example.com"
    assert identity.subject == "google-subject"
    assert identity.email_verified is False


def test_google_verifier_rejects_invalid_claims(monkeypatch):
    monkeypatch.setattr(
        "src.infrastructure.security.google_identity_verifier.id_token.verify_oauth2_token",
        lambda token, request, audience: {
            "iss": "malicious.example",
            "sub": "google-subject",
            "email": "user@example.com",
            "email_verified": True,
        },
    )

    with pytest.raises(ValueError, match="Jeton Google invalide"):
        GoogleIdTokenVerifier("google-client-id").verify("google-id-token")


def test_google_verifier_rejects_empty_subject(monkeypatch):
    monkeypatch.setattr(
        "src.infrastructure.security.google_identity_verifier.id_token.verify_oauth2_token",
        lambda token, request, audience: {
            "iss": "https://accounts.google.com",
            "sub": "",
            "email": "user@example.com",
            "email_verified": True,
        },
    )

    with pytest.raises(ValueError, match="Jeton Google invalide"):
        GoogleIdTokenVerifier("google-client-id").verify("google-id-token")
