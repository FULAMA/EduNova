"""
EduNova Integrations Module.

This module provides external service integrations following Clean Architecture:
- Domain: Entities and value objects
- Application: Use cases and interfaces
- Infrastructure: Concrete implementations

Supported Integrations:
- Notifications: Brevo, Courier, Firebase
- Payments: Stripe, Flutterwave
- Classroom: Google Classroom, Google Calendar
- LMS: Moodle
- Video Conference: Jitsi
- Analytics: PostHog
"""

from src.integrations.domain.entities.integration_provider import (
    IntegrationProvider,
    ProviderName,
    ProviderType,
    ProviderStatus,
)
from src.integrations.domain.entities.notification import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
)

__all__ = [
    # Domain Entities
    "IntegrationProvider",
    "ProviderName",
    "ProviderType",
    "ProviderStatus",
    "Notification",
    "NotificationChannel",
    "NotificationPriority",
    "NotificationStatus",
]
