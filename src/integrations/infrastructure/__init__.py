"""
Integrations Infrastructure Layer

Contains concrete implementations of external service integrations.

Principles:
- Implements application interfaces (ports)
- Handles external API calls
- Manages connection pooling and retries
- Logs and monitors external calls
- Respects rate limits and quotas
- Secrets are injected, never hardcoded
"""

__all__ = []
