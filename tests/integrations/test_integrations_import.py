"""
Test integrations module imports.
"""



def test_import_settings():
    """Test that Settings with integration fields can be imported."""
    from src.infrastructure.config.settings import Settings
    
    assert Settings is not None


def test_import_integration_entities():
    """Test that integration entities can be imported."""
    from src.integrations.domain.entities.integration_provider import IntegrationProvider
    from src.integrations.domain.entities.notification import (
        Notification,
        NotificationChannel,
        NotificationPriority,
        NotificationStatus,
    )
    
    assert IntegrationProvider is not None
    assert Notification is not None
    assert NotificationChannel is not None
    assert NotificationPriority is not None
    assert NotificationStatus is not None


def test_import_interfaces():
    """Test that integration interfaces can be imported."""
    from src.integrations.application.interfaces.notification_service import (
        NotificationService,
    )
    from src.integrations.application.interfaces.payment_gateway import (
        PaymentGateway,
        PaymentResult,
        PaymentStatus,
    )
    
    assert NotificationService is not None
    assert PaymentGateway is not None
    assert PaymentResult is not None
    assert PaymentStatus is not None


def test_import_services():
    """Test that integration services can be imported."""
    from src.integrations.infrastructure.services.brevo_notification_service import (
        BrevoNotificationService,
    )
    from src.integrations.infrastructure.services.courier_notification_service import (
        CourierNotificationService,
    )
    from src.integrations.infrastructure.services.firebase_notification_service import (
        FirebaseNotificationService,
    )
    from src.integrations.infrastructure.services.stripe_payment_gateway import (
        StripePaymentGateway,
    )
    from src.integrations.infrastructure.services.flutterwave_payment_gateway import (
        FlutterwavePaymentGateway,
    )
    from src.integrations.infrastructure.services.google_classroom_service import (
        GoogleClassroomService,
    )
    from src.integrations.infrastructure.services.google_calendar_service import (
        GoogleCalendarService,
    )
    from src.integrations.infrastructure.services.moodle_lms_service import (
        MoodleLMSService,
    )
    from src.integrations.infrastructure.services.jitsi_video_service import (
        JitsiVideoService,
    )
    from src.integrations.infrastructure.services.posthog_analytics_service import (
        PostHogAnalyticsService,
    )
    
    assert BrevoNotificationService is not None
    assert CourierNotificationService is not None
    assert FirebaseNotificationService is not None
    assert StripePaymentGateway is not None
    assert FlutterwavePaymentGateway is not None
    assert GoogleClassroomService is not None
    assert GoogleCalendarService is not None
    assert MoodleLMSService is not None
    assert JitsiVideoService is not None
    assert PostHogAnalyticsService is not None


def test_import_container():
    """Test that container with integration services can be imported."""
    from src.presentation.api.container import ApplicationContainer
    
    assert ApplicationContainer is not None


if __name__ == "__main__":
    # Run tests
    test_import_settings()
    print("✓ Settings import test passed")
    
    test_import_integration_entities()
    print("✓ Integration entities import test passed")
    
    test_import_interfaces()
    print("✓ Integration interfaces import test passed")
    
    test_import_services()
    print("✓ Integration services import test passed")
    
    test_import_container()
    print("✓ Container import test passed")
    
    print("\n✅ All integration import tests passed!")
