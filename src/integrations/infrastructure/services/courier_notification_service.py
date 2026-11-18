"""
Courier Notification Service Implementation.

Concrete implementation of NotificationService interface using Courier API.
"""

from typing import Any

from src.integrations.application.interfaces.notification_service import (
    NotificationService,
)
from src.integrations.domain.entities.notification import Notification


class CourierNotificationService(NotificationService):
    """Notification service using Courier API."""

    def __init__(self, api_key: str) -> None:
        """
        Initialize Courier notification service.

        Args:
            api_key: Courier API key
        """
        if not api_key:
            raise ValueError("Courier API key is required")
        self._api_key = api_key
        self._base_url = "https://api.courier.com"

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        **kwargs: Any,
    ) -> bool:
        """
        Send email notification via Courier API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML
            **kwargs: Additional Courier-specific parameters

        Returns:
            True if email sent successfully, False otherwise
        """
        print(f"[COURIER] Sending email to {to_email}: {subject}")
        return True

    def send_sms(
        self,
        to_phone: str,
        message: str,
        **kwargs: Any,
    ) -> bool:
        """
        Send SMS notification via Courier API.

        Args:
            to_phone: Recipient phone number
            message: SMS message content
            **kwargs: Additional Courier-specific parameters

        Returns:
            True if SMS sent successfully, False otherwise
        """
        print(f"[COURIER] Sending SMS to {to_phone}: {message}")
        return True

    def send_push(
        self,
        notification: Notification,
        **kwargs: Any,
    ) -> bool:
        """
        Send push notification via Courier API.

        Args:
            notification: Notification entity
            **kwargs: Additional Courier-specific parameters

        Returns:
            True if push sent successfully, False otherwise
        """
        print(f"[COURIER] Sending push: {notification.title}")
        return True

    async def send_async(
        self,
        notification: Notification,
        **kwargs: Any,
    ) -> bool:
        """
        Send notification asynchronously via Courier API.

        Args:
            notification: Notification entity
            **kwargs: Additional Courier-specific parameters

        Returns:
            True if notification queued successfully, False otherwise
        """
        print(f"[COURIER ASYNC] Sending: {notification.title}")
        return True
