"""
Test basic usage of integration services.
"""



def test_settings_has_integration_fields():
    """Test that Settings has all integration fields."""
    from src.infrastructure.config.settings import Settings
    from dataclasses import fields
    
    # Get all dataclass fields
    settings_fields = {f.name for f in fields(Settings)}
    
    integration_fields = {
        'brevo_api_key',
        'courier_api_key',
        'firebase_credentials_path',
        'stripe_secret_key',
        'stripe_webhook_secret',
        'stripe_publishable_key',
        'flutterwave_secret_key',
        'flutterwave_public_key',
        'flutterwave_encryption_key',
        'google_calendar_enabled',
        'google_classroom_enabled',
        'google_oauth_client_id',
        'google_oauth_client_secret',
        'moodle_base_url',
        'moodle_token',
        'jitsi_base_url',
        'posthog_project_id',
        'posthog_api_key',
        'posthog_base_url',
        'maintenance_mode',
    }
    
    for field in integration_fields:
        assert field in settings_fields, f"Field {field} not found in Settings dataclass"


def test_provider_name_enum():
    """Test ProviderName enum values."""
    from src.integrations.domain.entities.integration_provider import ProviderName
    
    expected_providers = [
        'brevo', 'courier', 'firebase',
        'stripe', 'flutterwave',
        'google_classroom', 'google_calendar',
        'moodle', 'jitsi', 'posthog'
    ]
    
    provider_values = [p.value for p in ProviderName]
    
    for provider in expected_providers:
        assert provider in provider_values, f"Provider {provider} not found"


def test_notification_entities():
    """Test notification entity creation."""
    from uuid import uuid4
    from src.integrations.domain.entities.notification import (
        Notification,
        NotificationChannel,
        NotificationPriority,
        NotificationStatus,
    )
    
    notification = Notification(
        id=uuid4(),
        tenant_id=uuid4(),
        channel=NotificationChannel.EMAIL,
        title="Test Notification",
        body="This is a test",
    )
    
    assert notification.id is not None
    assert notification.tenant_id is not None
    assert notification.channel == NotificationChannel.EMAIL
    assert notification.title == "Test Notification"
    assert notification.body == "This is a test"
    assert notification.priority == NotificationPriority.NORMAL
    assert notification.status == NotificationStatus.PENDING


def test_payment_interfaces():
    """Test payment interface classes."""
    from src.integrations.application.interfaces.payment_gateway import (
        PaymentRequest,
        PaymentResponse,
        PaymentStatus,
        PaymentMethod,
        Currency,
    )
    from uuid import uuid4
    from decimal import Decimal
    
    request = PaymentRequest(
        tenant_id=uuid4(),
        user_id=uuid4(),
        amount=Decimal("100.00"),
        currency=Currency.USD,
        method=PaymentMethod.CARD,
        description="Test payment",
        reference="test_ref_123",
    )
    
    assert request.tenant_id is not None
    assert request.amount == Decimal("100.00")
    assert request.currency == Currency.USD
    
    response = PaymentResponse(
        payment_id="pi_test_123",
        status=PaymentStatus.SUCCESS,
        reference="test_ref_123",
        amount=Decimal("100.00"),
        currency=Currency.USD,
    )
    
    assert response.payment_id == "pi_test_123"
    assert response.status == PaymentStatus.SUCCESS


def test_service_instantiation():
    """Test that services can be instantiated with mock data."""
    from src.integrations.infrastructure.services.brevo_notification_service import (
        BrevoNotificationService,
    )
    from src.integrations.infrastructure.services.stripe_payment_gateway import (
        StripePaymentGateway,
    )
    from src.integrations.infrastructure.services.google_classroom_service import (
        GoogleClassroomService,
    )
    
    # Test Brevo with mock API key
    brevo = BrevoNotificationService(api_key="mock_api_key")
    assert brevo is not None
    
    # Test Stripe with mock keys
    stripe = StripePaymentGateway(
        secret_key="sk_test_mock",
        webhook_secret="whsec_mock",
        publishable_key="pk_test_mock",
    )
    assert stripe is not None
    assert stripe.publishable_key == "pk_test_mock"
    
    # Test Google Classroom
    classroom = GoogleClassroomService(
        enabled=True,
        client_id="mock_client_id",
        client_secret="mock_client_secret",
    )
    assert classroom is not None
    assert classroom.is_enabled is True


def test_service_methods():
    """Test that service methods can be called."""
    from src.integrations.infrastructure.services.stripe_payment_gateway import (
        StripePaymentGateway,
    )
    from src.integrations.application.interfaces.payment_gateway import (
        PaymentRequest,
        PaymentStatus,
        Currency,
        PaymentMethod,
    )
    from uuid import uuid4
    from decimal import Decimal
    
    stripe = StripePaymentGateway(
        secret_key="sk_test_mock",
    )
    
    # Test create_payment_intent
    result = stripe.create_payment_intent(
        amount=Decimal("100.00"),
        currency="USD",
        description="Test payment",
    )
    assert result["success"] is True
    assert "payment_id" in result
    assert "client_secret" in result
    
    # Test process_payment (interface method)
    request = PaymentRequest(
        tenant_id=uuid4(),
        user_id=uuid4(),
        amount=Decimal("100.00"),
        currency=Currency.USD,
        method=PaymentMethod.CARD,
        description="Test",
        reference="ref_123",
    )
    response = stripe.process_payment(request)
    assert response.status == PaymentStatus.SUCCESS
    assert response.payment_id is not None


def test_container_integration():
    """Test that services can be accessed through the container."""
    from src.presentation.api.container import ApplicationContainer
    
    # Check that integration service methods exist on the class
    assert hasattr(ApplicationContainer, 'brevo_notification_service')
    assert hasattr(ApplicationContainer, 'stripe_payment_gateway')
    assert hasattr(ApplicationContainer, 'google_classroom_service')
    assert hasattr(ApplicationContainer, 'moodle_lms_service')
    assert hasattr(ApplicationContainer, 'jitsi_video_service')
    assert hasattr(ApplicationContainer, 'posthog_analytics_service')


if __name__ == "__main__":
    # Run tests
    test_settings_has_integration_fields()
    print("✓ Settings fields test passed")
    
    test_provider_name_enum()
    print("✓ ProviderName enum test passed")
    
    test_notification_entities()
    print("✓ Notification entities test passed")
    
    test_payment_interfaces()
    print("✓ Payment interfaces test passed")
    
    test_service_instantiation()
    print("✓ Service instantiation test passed")
    
    test_service_methods()
    print("✓ Service methods test passed")
    
    test_container_integration()
    print("✓ Container integration test passed")
    
    print("\n✅ All basic usage tests passed!")
