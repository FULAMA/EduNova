from fastapi.testclient import TestClient

from src.identity.application.use_cases.login_user import LoginUserResponse
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.tenant import TEST_TENANT_ID


class FakeGoogleLogin:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def execute(self, request):
        if self.error:
            raise ValueError(self.error)
        return self.result


def build_client(use_case):
    container = ApplicationContainer(database_path=":memory:")
    return TestClient(
        create_app(
            container=container,
            login_with_google_use_case=use_case,
        )
    )


def test_google_login_returns_edunova_session_tokens():
    client = build_client(
        FakeGoogleLogin(
            result=LoginUserResponse(
                authenticated=True,
                two_factor_required=False,
                two_factor_token=None,
                access_token="access-token",
                refresh_token="refresh-token",
            )
        )
    )

    response = client.post(
        "/auth/google",
        json={
            "id_token": "google-id-token",
            "tenant_id": str(TEST_TENANT_ID),
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "access-token"


def test_google_login_does_not_disclose_unknown_account_details():
    client = build_client(FakeGoogleLogin(error="Identifiants invalides."))

    response = client.post(
        "/auth/google",
        json={
            "id_token": "google-id-token",
            "tenant_id": str(TEST_TENANT_ID),
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentification Google refusee."
