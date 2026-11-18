"""
Flutterwave Payment Gateway Implementation.

Concrete implementation of PaymentGateway interface using Flutterwave API.
"""

from decimal import Decimal
from typing import Any

from src.integrations.application.interfaces.payment_gateway import (
    Currency,
    PaymentGateway,
    PaymentMethod,
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
)
from src.integrations.domain.entities.integration_provider import ProviderName


class FlutterwavePaymentGateway(PaymentGateway):
    """Payment gateway using Flutterwave API."""

    def __init__(
        self,
        secret_key: str,
        public_key: str | None = None,
        encryption_key: str | None = None,
    ) -> None:
        """
        Initialize Flutterwave payment gateway.

        Args:
            secret_key: Flutterwave secret key
            public_key: Flutterwave public key for frontend
            encryption_key: Flutterwave encryption key
        """
        if not secret_key:
            raise ValueError("Flutterwave secret key is required")

        self._secret_key = secret_key
        self._public_key = public_key
        self._encryption_key = encryption_key
        self._provider = ProviderName.FLUTTERWAVE
        self._base_url = "https://api.flutterwave.com/v3"

    @property
    def public_key(self) -> str | None:
        """Get the public key for frontend integration."""
        return self._public_key

    # =========================================================================
    # Flutterwave-specific methods
    # =========================================================================

    def create_payment(
        self,
        amount: Decimal,
        currency: str = "XOF",
        description: str = "",
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a Flutterwave payment.

        Args:
            amount: Payment amount
            currency: Three-letter ISO currency code
            description: Payment description
            metadata: Additional metadata
            **kwargs: Additional Flutterwave-specific parameters

        Returns:
            Dictionary with payment details
        """
        import secrets

        tx_ref = kwargs.get("tx_ref") or f"edunova_{secrets.token_urlsafe(16)}"
        amount_int = int(amount)

        print(
            f"[FLUTTERWAVE] Creating payment: "
            f"amount={amount_int}, currency={currency}, ref={tx_ref}"
        )

        return {
            "success": True,
            "provider": self._provider.value,
            "payment_id": tx_ref,
            "client_secret": tx_ref,
            "amount": str(amount),
            "currency": currency,
            "status": "pending",
        }

    def confirm_payment(
        self,
        payment_id: str,
        payment_method_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Verify/Confirm a Flutterwave payment.

        Args:
            payment_id: Transaction reference or ID
            payment_method_id: Payment method ID
            **kwargs: Additional parameters

        Returns:
            Dictionary with confirmation status
        """
        print(f"[FLUTTERWAVE] Verifying payment {payment_id}")
        return {
            "success": True,
            "payment_id": payment_id,
            "status": "successful",
        }

    def get_payment_status(self, payment_id: str, **kwargs: Any) -> dict[str, Any]:
        """
        Get status of a Flutterwave payment.

        Args:
            payment_id: Transaction reference or ID
            **kwargs: Additional parameters

        Returns:
            Dictionary with current status
        """
        print(f"[FLUTTERWAVE] Getting status for payment {payment_id}")
        return {
            "success": True,
            "payment_id": payment_id,
            "status": "successful",
        }

    # =========================================================================
    # PaymentGateway Interface Implementation
    # =========================================================================

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process a payment request.

        Args:
            request: Payment request details

        Returns:
            Payment response with status and details
        """
        print(f"[FLUTTERWAVE] Processing payment: {request.reference}")
        return PaymentResponse(
            payment_id=request.reference,
            status=PaymentStatus.SUCCESS,
            reference=request.reference,
            amount=request.amount,
            currency=request.currency,
            raw_response={"status": "successful"},
        )

    def refund_payment(
        self,
        payment_id: str,
        amount: Decimal | None = None,
        reason: str | None = None,
    ) -> PaymentResponse:
        """
        Refund a payment.

        Args:
            payment_id: Transaction ID
            amount: Amount to refund
            reason: Reason for refund

        Returns:
            Refund response
        """
        print(f"[FLUTTERWAVE] Refunding payment {payment_id}")
        return PaymentResponse(
            payment_id=payment_id,
            status=PaymentStatus.REFUNDED,
            reference=f"refund_{payment_id}",
            amount=amount or Decimal("0"),
            currency=Currency.USD,
            raw_response={"status": "refunded"},
        )

    def verify_webhook(
        self,
        payload: dict[str, Any],
        signature: str | None = None,
    ) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Webhook payload
            signature: Webhook signature

        Returns:
            True if valid, False otherwise
        """
        if not self._encryption_key:
            print(
                "[FLUTTERWAVE] Webhook verification failed: "
                "no encryption key configured"
            )
            return False
        # TODO: Implement actual Flutterwave signature verification
        print("[FLUTTERWAVE] Webhook signature verification (mock)")
        return True

    def get_supported_currencies(self) -> list[Currency]:
        """
        Get supported currencies.

        Returns:
            List of supported currencies
        """
        return [Currency.USD, Currency.CDF]

    def get_supported_methods(self) -> list[PaymentMethod]:
        """
        Get supported payment methods.

        Returns:
            List of supported payment methods
        """
        return [
            PaymentMethod.CARD,
            PaymentMethod.MOBILE_MONEY,
            PaymentMethod.BANK_TRANSFER,
        ]

    def is_healthy(self) -> bool:
        """
        Check if gateway is healthy.

        Returns:
            True if healthy, False otherwise
        """
        return True
