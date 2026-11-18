"""
Notification Domain Entities

Represents notifications to be sent via external providers.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class NotificationChannel(Enum):
    """Notification delivery channels."""
    
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """Notification priority levels."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """Notification delivery status."""
    
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass(frozen=True)
class Notification:
    """
    Represents a notification to be sent.
    
    Attributes:
        id: Unique identifier
        tenant_id: Tenant that owns this notification
        recipient_id: User ID of the recipient
        recipient_email: Email of the recipient (for email notifications)
        recipient_phone: Phone number (for SMS notifications)
        recipient_device_token: Device token (for push notifications)
        channel: Delivery channel
        priority: Priority level
        title: Notification title
        body: Notification body/content
        data: Additional data payload
        status: Current delivery status
        provider: Provider to use (optional)
        scheduled_at: When to send (None = immediate)
        created_at: When notification was created
        updated_at: When notification was last updated
    """
    
    id: UUID
    tenant_id: UUID
    channel: NotificationChannel
    title: str
    body: str
    recipient_id: UUID | None = None
    recipient_email: str | None = None
    recipient_phone: str | None = None
    recipient_device_token: str | None = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: dict | None = None
    status: NotificationStatus = NotificationStatus.PENDING
    provider: str | None = None
    scheduled_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Notification title cannot be empty.")
        if not self.body.strip():
            raise ValueError("Notification body cannot be empty.")
        if self.data is None:
            object.__setattr__(self, 'data', {})
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.now())
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', datetime.now())
