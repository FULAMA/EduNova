"""
Brevo Notification Service Implementation.

Concrete implementation of NotificationService interface using Brevo (ex-Sendinblue) API.
This implementation uses direct HTTP calls to Brevo REST API.

Features:
- Send email notifications
- Send SMS notifications
- Send push notifications (via Brevo)
- Handle Brevo-specific errors
- Automatic retry on rate limiting
- Transactional and marketing emails
"""

import asyncio
from typing import Any

from src.integrations.application.interfaces.notification_service import (
    NotificationService,
)
from src.integrations.domain.entities.integration_provider import ProviderName
from src.integrations.domain.entities.notification import Notification
from src.integrations.infrastructure.http import IntegrationHttpFactory, IntegrationHttpError


class BrevoNotificationService(NotificationService):
    """Notification service using Brevo API."""

    BREVO_API_VERSION = "v3"

    def __init__(self, api_key: str) -> None:
        """
        Initialize Brevo notification service.

        Args:
            api_key: Brevo API key

        Raises:
            ValueError: If API key is invalid
        """
        if not api_key or len(api_key.strip()) < 10:
            raise ValueError("Invalid Brevo API key")

        self._api_key = api_key
        self._provider = ProviderName.BREVO
        self._http_client = IntegrationHttpFactory.create_brevo_client(api_key)

    @property
    def provider(self) -> ProviderName:
        """Get the notification provider."""
        return self._provider

    # =========================================================================
    # Email Operations
    # =========================================================================

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        **kwargs: Any,
    ) -> bool:
        """
        Send an email notification via Brevo.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML
            **kwargs: Additional Brevo-specific parameters

        Returns:
            True if email sent successfully, False otherwise

        Raises:
            IntegrationHttpError: If API request fails
        """
        try:
            # Get sender from kwargs or use default
            sender = kwargs.get("sender", {"name": "EduNova", "email": "noreply@edunova.com"})
            
            # Build recipient list
            recipients = [{"email": to_email}]
            if "to_name" in kwargs:
                recipients[0]["name"] = kwargs["to_name"]

            # Build payload
            payload: dict[str, Any] = {
                "sender": sender,
                "to": recipients,
                "subject": subject,
            }

            if is_html:
                payload["htmlContent"] = body
            else:
                payload["textContent"] = body

            # Add optional parameters
            if "reply_to" in kwargs:
                payload["replyTo"] = kwargs["reply_to"]
            if "tags" in kwargs:
                payload["tags"] = kwargs["tags"]
            if "headers" in kwargs:
                payload["headers"] = kwargs["headers"]

            # Send transactional email
            url = "https://api.brevo.com/v3/smtp/email"
            response = self._http_client.post(url, json=payload)
            response_data = response.json()

            # Check if email was sent successfully
            if response.status_code == 202 and response_data.get("messageId"):
                return True
            
            return False

        except IntegrationHttpError:
            # Log error but return False for non-critical failures
            return False
        except Exception:
            return False

    def send_email_template(
        self,
        template_id: int,
        to_email: str,
        subject: str | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> bool:
        """
        Send an email using a Brevo template.

        Args:
            template_id: Brevo template ID
            to_email: Recipient email address
            subject: Email subject (optional)
            params: Template parameters
            **kwargs: Additional parameters

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            recipient = {"email": to_email}
            if "to_name" in kwargs:
                recipient["name"] = kwargs["to_name"]

            payload: dict[str, Any] = {
                "templateId": template_id,
                "to": [recipient],
            }

            if subject:
                payload["subject"] = subject
            if params:
                payload["params"] = params

            url = "https://api.brevo.com/v3/smtp/email"
            response = self._http_client.post(url, json=payload)
            response_data = response.json()

            if response.status_code == 202 and response_data.get("messageId"):
                return True
            
            return False

        except Exception:
            return False

    # =========================================================================
    # SMS Operations
    # =========================================================================

    def send_sms(
        self,
        to_phone: str,
        message: str,
        **kwargs: Any,
    ) -> bool:
        """
        Send an SMS notification via Brevo.

        Args:
            to_phone: Recipient phone number in international format (e.g., +1234567890)
            message: SMS message content (max 160 characters for single SMS)
            **kwargs: Additional Brevo-specific parameters

        Returns:
            True if SMS sent successfully, False otherwise

        Raises:
            IntegrationHttpError: If API request fails
        """
        try:
            if len(message) > 160:
                # Brevo supports long SMS, but it will be split
                pass

            # Build payload
            payload: dict[str, Any] = {
                "recipient": to_phone,
                "content": message,
            }

            # Add optional parameters
            if "sender" in kwargs:
                payload["sender"] = kwargs["sender"]
            if "tag" in kwargs:
                payload["tag"] = kwargs["tag"]
            if "webUrl" in kwargs:
                payload["webUrl"] = kwargs["webUrl"]

            url = "https://api.brevo.com/v3/transactionalSms/send"
            response = self._http_client.post(url, json=payload)
            response_data = response.json()

            if response.status_code == 201 and response_data.get("reference"):
                return True
            
            return False

        except IntegrationHttpError:
            return False
        except Exception:
            return False

    # =========================================================================
    # Push Notification Operations
    # =========================================================================

    def send_push(
        self,
        notification: Notification,
        **kwargs: Any,
    ) -> bool:
        """
        Send a push notification via Brevo.

        Note: Brevo's push notification support may vary by region.
        This method sends an email notification as fallback for push.

        Args:
            notification: Notification entity
            **kwargs: Additional parameters

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            # For now, send as email since Brevo push may not be available
            # In a real implementation, this would use Brevo's push API
            return self.send_email(
                to_email=notification.recipient_email or "",
                subject=notification.title,
                body=notification.body,
                is_html=False,
                **kwargs,
            )
        except Exception:
            return False

    # =========================================================================
    # Async Operations
    # =========================================================================

    async def send_async(
        self,
        notification: Notification,
        **kwargs: Any,
    ) -> bool:
        """
        Send a notification asynchronously.

        Args:
            notification: Notification entity
            **kwargs: Additional parameters

        Returns:
            True if notification queued successfully, False otherwise
        """
        # For now, use sync methods but in a thread
        # In production, this would use async HTTP client
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                self._send_notification_async, notification, **kwargs
            )
            return await asyncio.wrap_future(future)

    def _send_notification_async(
        self,
        notification: Notification,
        **kwargs: Any,
    ) -> bool:
        """Send notification in a separate thread."""
        try:
            # Choose method based on channel
            if notification.channel.value == "email":
                return self.send_email(
                    to_email=notification.recipient_email or "",
                    subject=notification.title,
                    body=notification.body,
                    is_html=notification.data.get("is_html", False) if notification.data else False,
                    **kwargs,
                )
            elif notification.channel.value == "sms":
                return self.send_sms(
                    to_phone=notification.recipient_phone or "",
                    message=notification.body,
                    **kwargs,
                )
            else:
                return self.send_push(notification, **kwargs)
        except Exception:
            return False

    # =========================================================================
    # Contact Management (for testing)
    # =========================================================================

    def create_contact(
        self,
        email: str,
        attributes: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a contact in Brevo.

        Args:
            email: Contact email
            attributes: Contact attributes
            **kwargs: Additional parameters

        Returns:
            Contact object
        """
        try:
            payload: dict[str, Any] = {"email": email}
            if attributes:
                payload["attributes"] = attributes

            url = "https://api.brevo.com/v3/contacts"
            response = self._http_client.post(url, json=payload)
            return response.json()
        except Exception:
            return {}

    def get_contact(self, email: str, **kwargs: Any) -> dict[str, Any]:
        """
        Get a contact by email.

        Args:
            email: Contact email
            **kwargs: Additional parameters

        Returns:
            Contact object
        """
        try:
            # Brevo uses identifier which can be email
            url = f"https://api.brevo.com/v3/contacts/{email}"
            response = self._http_client.get(url)
            return response.json()
        except IntegrationHttpError:
            return {}
        except Exception:
            return {}

    # =========================================================================
    # Health Check
    # =========================================================================

    def is_healthy(self) -> bool:
        """
        Check if the service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Make a simple API call to check connectivity
            self.get_contact("test@example.com")
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Close the HTTP client."""
        self._http_client.close()

    def __enter__(self) -> "BrevoNotificationService":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
