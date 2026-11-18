from unittest.mock import patch

import pytest

from src.infrastructure.security.google_identity_verifier import GoogleIdTokenVerifier


@patch("src.infrastructure.security.google_identity_verifier.id_token.verify_oauth2_token")
def test_google_id_token_requires_expected_nonce(verify_token):
    verify_token.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "google-subject",
        "email": "admin@example.test",
        "email_verified": True,
        "nonce": "issued-nonce",
    }

    identity = GoogleIdTokenVerifier("google-client-id").verify(
        "id-token", "issued-nonce"
    )
    assert identity.subject == "google-subject"

    with pytest.raises(ValueError, match="Jeton Google invalide"):
        GoogleIdTokenVerifier("google-client-id").verify("id-token", "other-nonce")
