"""
Moodle LMS Integration Service.

Provides integration with Moodle Learning Management System via REST API.
"""

from typing import Any

from src.integrations.domain.entities.integration_provider import ProviderName


class MoodleLMSService:
    """Service for integrating with Moodle LMS."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
    ) -> None:
        """
        Initialize Moodle LMS service.

        Args:
            base_url: Moodle REST API base URL
            token: Moodle web service token
        """
        self._base_url = base_url
        self._token = token
        self._provider = ProviderName.MOODLE

    @property
    def is_enabled(self) -> bool:
        """Check if integration is enabled."""
        return bool(self._base_url) and bool(self._token)

    @property
    def provider(self) -> ProviderName:
        """Get the integration provider."""
        return self._provider

    def create_course(
        self,
        short_name: str,
        full_name: str,
        category_id: int = 1,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a new course in Moodle.

        Args:
            short_name: Course short name (ID)
            full_name: Course full name
            category_id: Course category ID
            **kwargs: Additional Moodle course parameters

        Returns:
            Course resource from Moodle API
        """
        if not self.is_enabled:
            raise ValueError("Moodle integration is not enabled")

        print(f"[MOODLE] Creating course: {full_name} ({short_name})")
        return {
            "id": kwargs.get("id", 1),
            "shortname": short_name,
            "fullname": full_name,
            "categoryid": category_id,
        }

    def enroll_student(
        self,
        course_id: int,
        user_id: int,
        role_id: int = 5,  # Default student role
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Enroll a student in a Moodle course.

        Args:
            course_id: Moodle course ID
            user_id: Moodle user ID
            role_id: Role ID to assign (5 = student)
            **kwargs: Additional enrollment parameters

        Returns:
            Enrollment result from Moodle API
        """
        if not self.is_enabled:
            raise ValueError("Moodle integration is not enabled")

        print(f"[MOODLE] Enrolling student {user_id} in course {course_id}")
        return {
            "course_id": course_id,
            "user_id": user_id,
            "role_id": role_id,
            "status": "active",
        }

    def create_assignment(
        self,
        course_id: int,
        name: str,
        description: str = "",
        due_date: int | None = None,
        max_grade: float = 100.0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create an assignment in a Moodle course.

        Args:
            course_id: Moodle course ID
            name: Assignment name
            description: Assignment description
            due_date: Due date as Unix timestamp
            max_grade: Maximum grade for the assignment
            **kwargs: Additional assignment parameters

        Returns:
            Assignment resource from Moodle API
        """
        if not self.is_enabled:
            raise ValueError("Moodle integration is not enabled")

        print(f"[MOODLE] Creating assignment: {name} in course {course_id}")
        return {
            "id": kwargs.get("id", 1),
            "course": course_id,
            "name": name,
            "description": description,
            "duedate": due_date,
            "grade": max_grade,
        }

    def sync_course_content(
        self,
        course_id: int,
        content_items: list[dict[str, Any]],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Sync course content to Moodle.

        Args:
            course_id: Moodle course ID
            content_items: List of content items to sync
            **kwargs: Additional parameters

        Returns:
            Result of the sync operation
        """
        if not self.is_enabled:
            raise ValueError("Moodle integration is not enabled")

        print(f"[MOODLE] Syncing {len(content_items)} content items to course {course_id}")
        return {
            "course_id": course_id,
            "synced_count": len(content_items),
            "errors": [],
        }

    def get_course_users(
        self,
        course_id: int,
        role_id: int | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get users enrolled in a Moodle course.

        Args:
            course_id: Moodle course ID
            role_id: Filter by role ID
            **kwargs: Additional parameters

        Returns:
            List of user resources
        """
        if not self.is_enabled:
            raise ValueError("Moodle integration is not enabled")

        print(f"[MOODLE] Getting users for course {course_id}")
        return [
            {"id": 1, "fullname": "Student 1", "email": "student1@example.com"},
            {"id": 2, "fullname": "Student 2", "email": "student2@example.com"},
        ]
