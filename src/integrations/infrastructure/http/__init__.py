"""
HTTP Infrastructure for External Integrations.

Provides a shared HTTP client with common configuration for all external API calls.
"""

from src.integrations.infrastructure.http.integration_http_client import (
    IntegrationHttpClient,
    IntegrationHttpConfig,
    IntegrationHttpError,
)
from src.integrations.infrastructure.http.integration_http_factory import (
    IntegrationHttpFactory,
)

__all__ = [
    # Client
    "IntegrationHttpClient",
    "IntegrationHttpConfig",
    "IntegrationHttpError",
    # Factory
    "IntegrationHttpFactory",
]
