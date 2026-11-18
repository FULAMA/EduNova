"""
Integration HTTP Client Factory.

Creates pre-configured HTTP clients for each external integration service.
"""

from src.integrations.infrastructure.http.integration_http_client import (
    IntegrationHttpClient,
    IntegrationHttpConfig,
)


class IntegrationHttpFactory:
    """Factory for creating HTTP clients for external integrations."""

    @staticmethod
    def create_stripe_client(api_key: str) -> IntegrationHttpClient:
        """Create HTTP client for Stripe API."""
        config = IntegrationHttpConfig(
            base_url="https://api.stripe.com/v1",
            timeout=60.0,
            max_retries=3,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "EduNova/1.0",
            },
        )
        return IntegrationHttpClient(config)

    @staticmethod
    def create_brevo_client(api_key: str) -> IntegrationHttpClient:
        """Create HTTP client for Brevo API."""
        config = IntegrationHttpConfig(
            base_url="https://api.brevo.com/v3",
            timeout=30.0,
            max_retries=3,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
                "User-Agent": "EduNova/1.0",
            },
        )
        return IntegrationHttpClient(config)

    @staticmethod
    def create_courier_client(api_key: str) -> IntegrationHttpClient:
        """Create HTTP client for Courier API."""
        config = IntegrationHttpConfig(
            base_url="https://api.courier.com",
            timeout=30.0,
            max_retries=3,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "EduNova/1.0",
            },
        )
        return IntegrationHttpClient(config)

    @staticmethod
    def create_google_client(access_token: str) -> IntegrationHttpClient:
        """Create HTTP client for Google APIs."""
        config = IntegrationHttpConfig(
            timeout=30.0,
            max_retries=3,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": "EduNova/1.0",
            },
        )
        return IntegrationHttpClient(config)

    @staticmethod
    def create_moodle_client(token: str, base_url: str | None = None) -> IntegrationHttpClient:
        """Create HTTP client for Moodle REST API."""
        config = IntegrationHttpConfig(
            base_url=base_url or "https://moodle.example.com/webservice/rest/server.php",
            timeout=60.0,
            max_retries=3,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "EduNova/1.0",
            },
        )
        # Moodle uses token in query params, not headers
        return IntegrationHttpClient(config)

    @staticmethod
    def create_flutterwave_client(secret_key: str) -> IntegrationHttpClient:
        """Create HTTP client for Flutterwave API."""
        config = IntegrationHttpConfig(
            base_url="https://api.flutterwave.com/v3",
            timeout=60.0,
            max_retries=3,
            headers={
                "Authorization": f"Bearer {secret_key}",
                "Content-Type": "application/json",
                "User-Agent": "EduNova/1.0",
            },
        )
        return IntegrationHttpClient(config)

    @staticmethod
    def create_jitsi_client(base_url: str | None = None) -> IntegrationHttpClient:
        """Create HTTP client for Jitsi API."""
        config = IntegrationHttpConfig(
            base_url=base_url or "https://meet.jit.si",
            timeout=30.0,
            max_retries=3,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "EduNova/1.0",
            },
        )
        return IntegrationHttpClient(config)

    @staticmethod
    def create_posthog_client(api_key: str, base_url: str | None = None) -> IntegrationHttpClient:
        """Create HTTP client for PostHog API."""
        config = IntegrationHttpConfig(
            base_url=base_url or "https://app.posthog.com",
            timeout=30.0,
            max_retries=3,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "EduNova/1.0",
            },
        )
        return IntegrationHttpClient(config)

    @staticmethod
    def create_firebase_client(credentials_path: str | None = None) -> IntegrationHttpClient:
        """Create HTTP client for Firebase."""
        config = IntegrationHttpConfig(
            base_url="https://fcm.googleapis.com/fcm",
            timeout=30.0,
            max_retries=3,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "EduNova/1.0",
            },
        )
        return IntegrationHttpClient(config)
