# Integrations Module

> **Status:** Phase 0 - Preparation  
> **Created:** 2025-01-XX  
> **Reference:** [EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md](../../docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md)  
> **Gap Analysis:** [INTEGRATIONS_GAP_ANALYSIS.md](../../docs/integrations/INTEGRATIONS_GAP_ANALYSIS.md)

---

## 🎯 Overview

This module provides **external service integrations** for EduNova following **Clean Architecture** principles.

### Core Principles

1. **EduNova is the System of Record** - External services are adapters, not the source of truth
2. **Tenant Isolation** - All operations are scoped to a tenant
3. **Server-Side Secrets** - No secrets in frontend, repository, or version control
4. **Graceful Failures** - Retry, fallback, circuit breaker patterns
5. **Async-Capable** - All external calls support async/await
6. **Observable** - Logging, monitoring, and tracing for all external calls

---

## 📁 Module Structure

```
src/integrations/
├── __init__.py                    # Module exports
├── README.md                      # This file
│
├── domain/                        # Domain Layer
│   ├── __init__.py
│   └── entities/
│       ├── __init__.py
│       ├── integration_provider.py  # Provider configuration
│       └── notification.py         # Notification entity
│
├── application/                   # Application Layer
│   ├── __init__.py
│   ├── interfaces/                # Ports (Abstract Interfaces)
│   │   ├── __init__.py
│   │   ├── notification_service.py
│   │   └── payment_gateway.py
│   └── use_cases/                 # Use Cases (will be added)
│       └── __init__.py
│
└── infrastructure/               # Infrastructure Layer
    ├── __init__.py
    ├── services/                  # External Service Clients
    │   └── __init__.py
    └── repositories/              # Persistence
        └── __init__.py
```

---

## 🏗️ Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│              Frontend                   │
│         (React/Vite/TypeScript)          │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│           Presentation Layer             │
│         (FastAPI Routes/Controllers)      │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│           Application Layer              │
│         (Use Cases, Interfaces)          │ ← YOU ARE HERE
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│              Domain Layer                │
│          (Entities, Value Objects)       │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│          Infrastructure Layer             │
│    (External Services, Repositories)      │
└─────────────────────────────────────────┘
```

---

## 🔧 Current Implementation Status

### ✅ Phase 0 - Preparation (IN PROGRESS)

- [x] Created module structure (`src/integrations/`)
- [x] Created domain entities (`IntegrationProvider`, `Notification`)
- [x] Created service interfaces (`NotificationService`, `PaymentGateway`)
- [ ] Extend `Settings` for integration secrets
- [ ] Register services in Container DI
- [ ] Add tests for new entities/interfaces

### ⏳ Phase 1 - Core Integration Module

- [ ] Implement `IntegrationProviderRepository`
- [ ] Implement base `NotificationService`
- [ ] Implement base `PaymentGateway`
- [ ] Add dependency injection registration
- [ ] Add comprehensive tests

### 📋 Phases 2-8 - Individual Integrations

See [EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md](../../docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md) for details.

---

## 🎯 Integration Capabilities

### 1. Notifications 📧
**Status:** ❌ Not Implemented  
**Priority:** ⭐⭐⭐⭐⭐  
**Providers:** Brevo, Courier  
**Use Cases:** SendEmail, SendSMS, SendBatch

### 2. Push Notifications 📱
**Status:** ❌ Not Implemented  
**Priority:** ⭐⭐⭐⭐⭐  
**Providers:** Firebase FCM  
**Use Cases:** RegisterDevice, SendPush, SendBatch

### 3. Calendar Sync 📅
**Status:** ❌ Not Implemented  
**Priority:** ⭐⭐⭐⭐  
**Providers:** Google Calendar  
**Use Cases:** SyncEvent, DeleteEvent, ListEvents

### 4. Learning Management Systems 🎓
**Status:** ❌ Not Implemented  
**Priority:** ⭐⭐⭐  
**Providers:** Google Classroom, Moodle  
**Use Cases:** SyncClass, SyncAssignment, SyncGrade

### 5. Virtual Classrooms 💻
**Status:** ❌ Not Implemented  
**Priority:** ⭐⭐⭐  
**Providers:** Jitsi Meet  
**Use Cases:** CreateMeeting, GetMeeting, ListMeetings

### 6. Payments 💳
**Status:** ❌ Not Implemented  
**Priority:** ⭐⭐⭐⭐⭐ (Flutterwave for DRC)  
**Providers:** Stripe, Flutterwave  
**Use Cases:** ProcessPayment, RefundPayment, WebhookHandler

### 7. Analytics 📊
**Status:** ❌ Not Implemented  
**Priority:** ⭐⭐  
**Providers:** PostHog  
**Use Cases:** TrackEvent, IdentifyUser, GetMetrics

---

## 📦 Dependencies

### Python Dependencies (to be installed when needed)

```bash
# Notifications
pip install brevo-python courier-python

# Push Notifications
pip install firebase-admin

# Google APIs
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Payments
pip install stripe-python flutterwave-python

# Analytics
pip install posthog-python
```

### Frontend Dependencies (to be installed when needed)

```bash
# Firebase (Push + Analytics)
npm install firebase

# PostHog
npm install posthog-js
```

---

## 🛠️ Development Guidelines

### 1. Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Entity | PascalCase | `Notification`, `PaymentRequest` |
| Interface | PascalCase + "Service" | `NotificationService` |
| Use Case | PascalCase + Verb | `SendEmail`, `ProcessPayment` |
| Repository | PascalCase + "Repository" | `NotificationRepository` |
| Service (Infrastructure) | PascalCase + "Service" | `BrevoService`, `FirebaseService` |

### 2. Error Handling

- Use domain-specific exceptions
- Wrap external service errors
- Never expose sensitive information
- Implement retry with exponential backoff
- Log all failures (without PII)

### 3. Testing

- Unit tests for all use cases
- Integration tests with mocked services
- End-to-end tests with real APIs (test mode)
- Test tenant isolation
- Test error scenarios

### 4. Configuration

- All secrets in environment variables
- Prefix with `EDUNOVA_`
- Example: `EDUNOVA_BREVO_API_KEY`
- Never commit secrets to repository

---

## 📝 Adding a New Integration

### Step 1: Define Domain Entity (if needed)

```python
# src/integrations/domain/entities/new_entity.py
from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class NewEntity:
    id: UUID
    tenant_id: UUID
    # ... other fields
```

### Step 2: Define Service Interface

```python
# src/integrations/application/interfaces/new_service.py
from abc import ABC, abstractmethod
from uuid import UUID

class NewService(ABC):
    @abstractmethod
    async def do_something(self, tenant_id: UUID, ...) -> ...:
        raise NotImplementedError
```

### Step 3: Implement Infrastructure Service

```python
# src/integrations/infrastructure/services/new_service_impl.py
from src.integrations.application.interfaces.new_service import NewService

class RealNewService(NewService):
    def __init__(self, settings, http_client):
        self._settings = settings
        self._http_client = http_client
    
    async def do_something(self, tenant_id: UUID, ...) -> ...:
        # Implementation
        pass
```

### Step 4: Register in Container

```python
# src/presentation/api/container.py
from src.integrations.infrastructure.services.new_service_impl import RealNewService

class ApplicationContainer:
    def new_service(self) -> NewService:
        return RealNewService(
            settings=self._settings,
            http_client=self._http_client(),
        )
```

### Step 5: Add Tests

```python
# tests/unit/integrations/infrastructure/services/test_new_service.py
import pytest
from unittest.mock import AsyncMock
from src.integrations.infrastructure.services.new_service_impl import RealNewService

async def test_do_something():
    settings = ...
    http_client = AsyncMock()
    service = RealNewService(settings, http_client)
    
    result = await service.do_something(tenant_id, ...)
    assert result is not None
```

---

## 🔍 Monitoring and Observability

All integrations should:

1. **Log all external calls** (without sensitive data)
2. **Track metrics** (success/failure rates, latency)
3. **Support distributed tracing** (correlation IDs)
4. **Implement health checks** (is_healthy() method)
5. **Handle rate limits** (retry with backoff)

---

## 🚨 Security Considerations

1. **Never store secrets in code** - Use environment variables
2. **Validate all inputs** - Prevent injection attacks
3. **Use HTTPS** - All external calls must be encrypted
4. **Limit scope** - Use minimal OAuth scopes
5. **Verify webhooks** - Always verify signatures
6. **Rate limiting** - Protect against abuse
7. **Tenant isolation** - Never mix data between tenants

---

## 📚 Documentation

- [Plan Directeur d'Intégration](../../docs/integrations/EDUNOVA_EXTERNAL_INTEGRATIONS_IMPLEMENTATION_PLAN.md)
- [Analyse des Écarts](../../docs/integrations/INTEGRATIONS_GAP_ANALYSIS.md)
- [Registre des Décisions Métier](../../docs/decisions/REGISTRE_DECISIONS_METIER_EDUNOVA.md)

---

## 🎉 Next Steps

1. **Complete Phase 0**
   - Extend `Settings` for integration secrets
   - Register services in Container DI
   - Add tests for new entities/interfaces

2. **Start Phase 1** (Core Integration Module)
   - Implement repositories
   - Implement base services
   - Add comprehensive tests

3. **Start Phase 2** (Notifications)
   - Integrate Brevo or Courier
   - Implement notification use cases
   - Add frontend integration

---

**Status:** ✅ Phase 0 Structure Created  
**Next:** Extend Settings and Container DI  
**Owner:** Development Team  
**Last Updated:** 2025-01-XX
