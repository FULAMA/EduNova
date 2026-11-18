"""
Integration Provider Entity

Represents an external service provider with configuration.
"""

from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class ProviderName(Enum):
    """Supported integration provider names."""
    
    BREVO = "brevo"
    COURIER = "courier"
    FIREBASE = "firebase"
    STRIPE = "stripe"
    FLUTTERWAVE = "flutterwave"
    GOOGLE_CLASSROOM = "google_classroom"
    GOOGLE_CALENDAR = "google_calendar"
    MOODLE = "moodle"
    JITSI = "jitsi"
    POSTHOG = "posthog"


class ProviderType(Enum):
    """Supported integration provider types."""
    
    NOTIFICATION = "notification"  # Email/SMS providers (Brevo, Courier)
    PUSH = "push"  # Push notification providers (Firebase FCM)
    CALENDAR = "calendar"  # Calendar providers (Google Calendar)
    LMS = "lms"  # Learning Management Systems (Google Classroom, Moodle)
    VIRTUAL_CLASSROOM = "virtual_classroom"  # Virtual classroom (Jitsi)
    PAYMENT = "payment"  # Payment gateways (Stripe, Flutterwave)
    ANALYTICS = "analytics"  # Analytics (PostHog)


class ProviderStatus(Enum):
    """Status of an integration provider."""
    
    DISABLED = "disabled"
    ENABLED = "enabled"
    SUSPENDED = "suspended"
    ERROR = "error"


@dataclass(frozen=True)
class IntegrationProvider:
    """
    Represents an external service provider configuration.
    
    Attributes:
        id: Unique identifier
        tenant_id: Tenant that owns this configuration
        provider_type: Type of provider (notification, payment, etc.)
        provider_name: Name of the provider (brevo, stripe, etc.)
        status: Current status
        config: Provider-specific configuration (encrypted)
        webhook_url: URL for receiving webhooks (optional)
        webhook_secret: Secret for verifying webhooks (optional)
    """
    
    id: UUID
    tenant_id: UUID
    provider_type: ProviderType
    provider_name: str
    status: ProviderStatus = ProviderStatus.DISABLED
    config: dict | None = None
    webhook_url: str | None = None
    webhook_secret: str | None = None
    
    def __post_init__(self) -> None:
        if not self.provider_name.strip():
            raise ValueError("Provider name cannot be empty.")
        if self.config is None:
            object.__setattr__(self, 'config', {})
