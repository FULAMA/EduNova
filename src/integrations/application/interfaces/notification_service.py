"""
Notification Service Interface

Abstract interface for sending notifications via external providers.
"""

from abc import ABC, abstractmethod
from typing import Any

from src.integrations.domain.entities.notification import Notification


class NotificationService(ABC):
    """
    Abstract base class for notification services.
    
    Implementations must:
    - Respect tenant isolation
    - Handle failures gracefully
    - Support retry with exponential backoff
    - Log all attempts (without sensitive data)
    - Respect rate limits
    """
    
    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        **kwargs: Any,
    ) -> bool:
        """
        Send an email notification.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML
            **kwargs: Provider-specific parameters
            
        Returns:
            True if email sent successfully, False otherwise
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If sending fails
        """
        raise NotImplementedError
    
    @abstractmethod
    def send_sms(
        self,
        to_phone: str,
        message: str,
        **kwargs: Any,
    ) -> bool:
        """
        Send an SMS notification.
        
        Args:
            to_phone: Recipient phone number
            message: SMS message content
            **kwargs: Provider-specific parameters
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def send_push(
        self,
        notification: Notification,
        **kwargs: Any,
    ) -> bool:
        """
        Send a push notification.
        
        Args:
            notification: Notification entity
            **kwargs: Provider-specific parameters
            
        Returns:
            True if push sent successfully, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    async def send_async(
        self,
        notification: Notification,
        **kwargs: Any,
    ) -> bool:
        """
        Send a notification asynchronously.
        
        Args:
            notification: Notification entity
            **kwargs: Provider-specific parameters
            
        Returns:
            True if notification queued successfully, False otherwise
        """
        raise NotImplementedError
