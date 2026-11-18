"""
Jitsi Video Conference Service.

Provides integration with Jitsi Meet for video conferencing.
"""

import secrets
from typing import Any

from src.integrations.domain.entities.integration_provider import ProviderName


class JitsiVideoService:
    """Service for integrating with Jitsi Meet."""

    def __init__(self, base_url: str | None = None) -> None:
        """
        Initialize Jitsi video service.

        Args:
            base_url: Jitsi Meet server base URL (e.g., https://meet.jit.si)
        """
        self._base_url = base_url or "https://meet.jit.si"
        self._provider = ProviderName.JITSI

    @property
    def is_enabled(self) -> bool:
        """Check if integration is enabled."""
        return bool(self._base_url)

    @property
    def provider(self) -> ProviderName:
        """Get the integration provider."""
        return self._provider

    @property
    def base_url(self) -> str:
        """Get the Jitsi server base URL."""
        return self._base_url

    def create_room(
        self,
        name: str | None = None,
        options: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Create a new Jitsi meeting room.

        Args:
            name: Room name (optional, random name generated if None)
            options: Jitsi meeting options (config, interfaceConfig, etc.)
            **kwargs: Additional parameters

        Returns:
            Room URL or room name/ID
        """
        if not self.is_enabled:
            raise ValueError("Jitsi integration is not enabled")

        room_name = name or f"edunova_{secrets.token_urlsafe(8)}"
        # Clean room name for Jitsi (alphanumeric, hyphens, underscores)
        room_name = "".join(
            c if c.isalnum() or c in "-_." else "_"
            for c in room_name.lower()
        )

        room_url = f"{self._base_url}/{room_name}"
        print(f"[JITSI] Created room: {room_url}")
        return room_url

    def generate_room_token(
        self,
        room_name: str,
        user_id: str | None = None,
        user_name: str | None = None,
        moderator: bool = False,
        **kwargs: Any,
    ) -> str | None:
        """
        Generate a JWT token for a Jitsi room (requires JWT app in Jitsi).

        Args:
            room_name: Room name/ID
            user_id: User ID for the token
            user_name: User display name
            moderator: Whether user is a moderator
            **kwargs: Additional JWT parameters

        Returns:
            JWT token string or None if not configured
        """
        if not self.is_enabled:
            raise ValueError("Jitsi integration is not enabled")

        # This would require JWT secret configuration in a real implementation
        # For now, return None as JWT is optional
        print(f"[JITSI] Generating token for room {room_name} (user: {user_name})")
        return None

    def get_room_info(
        self,
        room_name: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get information about a Jitsi room.

        Note: This requires Jitsi REST API or external monitoring.

        Args:
            room_name: Room name/ID
            **kwargs: Additional parameters

        Returns:
            Room information dictionary
        """
        if not self.is_enabled:
            raise ValueError("Jitsi integration is not enabled")

        print(f"[JITSI] Getting info for room {room_name}")
        return {
            "room_name": room_name,
            "room_url": f"{self._base_url}/{room_name}",
            "participants": [],  # Would require actual API integration
        }

    def create_scheduled_meeting(
        self,
        title: str,
        start_time: str,
        duration_minutes: int = 60,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a scheduled meeting (requires Jitsi with calendar integration).

        Args:
            title: Meeting title
            start_time: Start time in ISO format
            duration_minutes: Meeting duration in minutes
            **kwargs: Additional parameters

        Returns:
            Meeting information with room URL
        """
        if not self.is_enabled:
            raise ValueError("Jitsi integration is not enabled")

        room_name = f"edunova_{secrets.token_urlsafe(8)}"
        room_url = f"{self._base_url}/{room_name}"

        print(
            f"[JITSI] Creating scheduled meeting: {title} "
            f"(room: {room_url}, starts: {start_time})"
        )
        return {
            "title": title,
            "room_name": room_name,
            "room_url": room_url,
            "start_time": start_time,
            "duration_minutes": duration_minutes,
        }
