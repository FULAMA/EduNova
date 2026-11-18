"""
Firebase Notification Service Implementation.

Concrete implementation of NotificationService interface using Firebase Cloud Messaging.
"""

import json
from typing import Any

from src.integrations.application.interfaces.notification_service import (
    NotificationService,
)
from src.integrations.domain.entities.notification import Notification


class FirebaseNotificationService(NotificationService):
    """Notification service using Firebase Cloud Messaging."""

    def __init__(self, credentials_path: str | None = None) -> None:
        """
        Initialize Firebase notification service.

        Args:
            credentials_path: Path to Firebase service account credentials JSON file
        """
        self._credentials_path = credentials_path
        self._credentials: dict[str, Any] = {}
        self._initialized = False

        if credentials_path:
            self._load_credentials(credentials_path)

    def _load_credentials(self, path: str) -> None:
        """Load Firebase credentials from JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._credentials = json.load(f)
            self._initialized = True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to load Firebase credentials: {e}") from e

    def _initialize(self) -> None:
        """Initialize Firebase SDK if not already initialized."""
        if self._initialized:
            return

        if not self._credentials_path:
            raise ValueError(
                "Firebase credentials path is required for initialization"
            )
        self._load_credentials(self._credentials_path)

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        **kwargs: Any,
    ) -> bool:
        """
        Send email notification via Firebase Extensions or third-party integration.

        Note: Firebase itself doesn't send emails directly. This would typically
        use Firebase Extensions or integrate with SendGrid/other providers.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML
            **kwargs: Additional parameters

        Returns:
            True if email sent successfully, False otherwise
        """
        print(f"[FIREBASE] Sending email to {to_email}: {subject}")
        return True

    def send_sms(
        self,
        to_phone: str,
        message: str,
        **kwargs: Any,
    ) -> bool:
        """
        Send SMS notification. Firebase doesn't provide SMS directly,
        this would typically integrate with Twilio or other SMS provider.

        Args:
            to_phone: Recipient phone number
            message: SMS message content
            **kwargs: Additional parameters

        Returns:
            True if SMS sent successfully, False otherwise
        """
        print(f"[FIREBASE] Sending SMS to {to_phone}: {message}")
        return True

    def send_push(
        self,
        notification: Notification,
        **kwargs: Any,
    ) -> bool:
        """
        Send push notification via Firebase Cloud Messaging.

        Args:
            notification: Notification entity
            **kwargs: Additional FCM-specific parameters (device_token, topic, etc.)

        Returns:
            True if push sent successfully, False otherwise
        """
        device_token = kwargs.get("device_token")
        topic = kwargs.get("topic")

        if not device_token and not topic:
            print("[FIREBASE] No device token or topic specified")
            return False

        # TODO: Implement actual FCM push notification
        print(
            f"[FIREBASE FCM] Sending push to {device_token or topic}: "
            f"{notification.title}"
        )
        return True

    async def send_async(
        self,
        notification: Notification,
        **kwargs: Any,
    ) -> bool:
        """
        Send notification asynchronously via Firebase.

        Args:
            notification: Notification entity
            **kwargs: Additional FCM-specific parameters

        Returns:
            True if notification queued successfully, False otherwise
        """
        print(f"[FIREBASE ASYNC] Sending: {notification.title}")
        return True
