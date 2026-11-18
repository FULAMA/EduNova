"""
Payment Gateway Interface

Abstract interface for processing payments via external providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID


class PaymentStatus(Enum):
    """Payment processing status."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    """Supported payment methods."""
    
    CARD = "card"
    MOBILE_MONEY = "mobile_money"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"


class Currency(Enum):
    """Supported currencies."""
    
    USD = "USD"
    CDF = "CDF"
    EUR = "EUR"


class PaymentRequest:
    """Request for payment processing."""
    
    def __init__(
        self,
        tenant_id: UUID,
        user_id: UUID,
        amount: Decimal,
        currency: Currency,
        method: PaymentMethod,
        description: str,
        reference: str,
        metadata: dict | None = None,
        callback_url: str | None = None,
    ):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.amount = amount
        self.currency = currency
        self.method = method
        self.description = description
        self.reference = reference
        self.metadata = metadata or {}
        self.callback_url = callback_url


class PaymentResponse:
    """Response from payment processing."""
    
    def __init__(
        self,
        payment_id: str,
        status: PaymentStatus,
        reference: str,
        amount: Decimal,
        currency: Currency,
        raw_response: dict | None = None,
    ):
        self.payment_id = payment_id
        self.status = status
        self.reference = reference
        self.amount = amount
        self.currency = currency
        self.raw_response = raw_response or {}


@dataclass
class PaymentResult:
    """
    Result of a payment operation.
    
    This is a more flexible result class that can be used for various
    payment operations including payment intents, confirmations, captures, and refunds.
    
    Attributes:
        success: Whether the operation was successful
        provider: Payment provider (e.g., STRIPE, FLUTTERWAVE)
        payment_id: Payment ID or transaction reference
        client_secret: Client secret for frontend integration (Stripe)
        amount: Payment amount
        currency: Currency code
        status: Payment status
        raw_response: Raw response from the payment provider
    """
    
    success: bool
    provider: str
    payment_id: str
    client_secret: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    status: str | None = None
    raw_response: dict[str, Any] | None = None


class PaymentGateway(ABC):
    """
    Abstract base class for payment gateway services.
    
    Implementations must:
    - Respect tenant isolation
    - Handle failures gracefully
    - Support webhook verification
    - Log all transactions (without sensitive data)
    - Respect PCI DSS compliance
    - Handle currency conversion if needed
    """
    
    @abstractmethod
    def process_payment(
        self,
        request: PaymentRequest,
    ) -> PaymentResponse:
        """
        Process a payment request.
        
        Args:
            request: Payment request details
            
        Returns:
            Payment response with status and details
            
        Raises:
            ValueError: If request is invalid
            RuntimeError: If processing fails
        """
        raise NotImplementedError
    
    @abstractmethod
    def refund_payment(
        self,
        payment_id: str,
        amount: Decimal | None = None,
        reason: str | None = None,
    ) -> PaymentResponse:
        """
        Refund a payment (full or partial).
        
        Args:
            payment_id: ID of the payment to refund
            amount: Amount to refund (None = full refund)
            reason: Reason for refund
            
        Returns:
            Refund response
        """
        raise NotImplementedError
    
    @abstractmethod
    def verify_webhook(
        self,
        payload: dict,
        signature: str | None = None,
    ) -> bool:
        """
        Verify a webhook payload and signature.
        
        Args:
            payload: Webhook payload
            signature: Webhook signature
            
        Returns:
            True if valid, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_supported_currencies(self) -> list[Currency]:
        """
        Get the list of supported currencies.
        
        Returns:
            List of supported currencies
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_supported_methods(self) -> list[PaymentMethod]:
        """
        Get the list of supported payment methods.
        
        Returns:
            List of supported payment methods
        """
        raise NotImplementedError
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """
        Check if the gateway is healthy and available.
        
        Returns:
            True if healthy, False otherwise
        """
        raise NotImplementedError
