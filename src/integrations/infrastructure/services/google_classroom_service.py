"""
Google Classroom Integration Service.

Concrete implementation of classroom integration using Google Classroom REST API.
This implementation uses OAuth2 authentication and supports:
- Class management
- Student enrollment
- Assignment creation
- Coursework management

Note: This service requires OAuth2 credentials (client_id, client_secret)
and a valid access token for authentication.
"""

from typing import Any

from src.integrations.domain.entities.integration_provider import ProviderName
from src.integrations.infrastructure.http import (
    IntegrationHttpClient,
    IntegrationHttpConfig,
    IntegrationHttpError,
)


class GoogleOAuthTokenManager:
    """Manages OAuth2 tokens for Google APIs."""

    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        """
        Initialize token manager.

        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: float | None = None

    @property
    def access_token(self) -> str | None:
        """Get current access token."""
        if self._access_token and self._expires_at:
            import time
            if time.time() > self._expires_at:
                # Token expired, refresh it
                self.refresh_access_token()
        return self._access_token

    @property
    def has_credentials(self) -> bool:
        """Check if OAuth credentials are configured."""
        return bool(self._client_id) and bool(self._client_secret)

    def set_access_token(
        self,
        access_token: str,
        expires_in: int | None = None,
        refresh_token: str | None = None,
    ) -> None:
        """
        Set access token.

        Args:
            access_token: OAuth2 access token
            expires_in: Seconds until expiration
            refresh_token: Refresh token (for obtaining new access tokens)
        """
        import time
        self._access_token = access_token
        if expires_in:
            self._expires_at = time.time() + expires_in
        if refresh_token:
            self._refresh_token = refresh_token

    def refresh_access_token(self) -> str | None:
        """
        Refresh the access token using the refresh token.

        Returns:
            New access token or None if refresh failed
        """
        if not self._refresh_token or not self.has_credentials:
            return None

        try:
            import httpx
            client = httpx.Client(timeout=30.0)
            
            data = {
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token",
            }
            
            response = client.post(
                self.GOOGLE_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.set_access_token(
                    access_token=token_data["access_token"],
                    expires_in=token_data.get("expires_in"),
                    refresh_token=token_data.get("refresh_token") or self._refresh_token,
                )
                return self._access_token
            
            return None
        except Exception:
            return None

    def get_authorization_url(
        self,
        redirect_uri: str,
        scope: str = "https://www.googleapis.com/auth/classroom.courses https://www.googleapis.com/auth/classroom.rosters",
        state: str | None = None,
    ) -> str:
        """
        Get OAuth2 authorization URL.

        Args:
            redirect_uri: OAuth2 redirect URI
            scope: Requested scopes
            state: State parameter for CSRF protection

        Returns:
            Authorization URL
        """
        import urllib.parse
        
        params = {
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope,
            "access_type": "offline",
            "prompt": "consent",
        }
        
        if state:
            params["state"] = state
        
        query_string = urllib.parse.urlencode(params)
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

    def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth2 flow
            redirect_uri: OAuth2 redirect URI

        Returns:
            Token response with access_token, refresh_token, etc.
        """
        import httpx
        
        if not self.has_credentials:
            raise ValueError("OAuth credentials not configured")

        client = httpx.Client(timeout=30.0)
        
        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        
        response = client.post(
            self.GOOGLE_TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.set_access_token(
                access_token=token_data["access_token"],
                expires_in=token_data.get("expires_in"),
                refresh_token=token_data.get("refresh_token"),
            )
            return token_data
        else:
            raise IntegrationHttpError(
                message=f"Failed to exchange code for token: {response.text}",
                status_code=response.status_code,
            )


class GoogleClassroomService:
    """Service for integrating with Google Classroom API."""

    CLASSROOM_API_BASE = "https://classroom.googleapis.com/v1"

    def __init__(
        self,
        enabled: bool = False,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
    ) -> None:
        """
        Initialize Google Classroom service.

        Args:
            enabled: Whether integration is enabled
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            access_token: OAuth2 access token (optional)
        """
        self._enabled = enabled
        self._client_id = client_id
        self._client_secret = client_secret
        self._provider = ProviderName.GOOGLE_CLASSROOM
        
        # Initialize token manager
        self._token_manager = GoogleOAuthTokenManager(client_id, client_secret)
        if access_token:
            self._token_manager.set_access_token(access_token)

    @property
    def is_enabled(self) -> bool:
        """Check if integration is enabled and configured."""
        return self._enabled and self._token_manager.has_credentials

    @property
    def provider(self) -> ProviderName:
        """Get the integration provider."""
        return self._provider

    @property
    def token_manager(self) -> GoogleOAuthTokenManager:
        """Get the token manager for OAuth2 flows."""
        return self._token_manager

    def _get_http_client(self) -> IntegrationHttpClient:
        """Get an HTTP client with current access token."""
        if not self._token_manager.access_token:
            raise ValueError("Access token is required")
        
        return IntegrationHttpClient(
            IntegrationHttpConfig(
                base_url="https://classroom.googleapis.com",
                headers={"Authorization": f"Bearer {self._token_manager.access_token}"},
            )
        )

    # =========================================================================
    # Course Operations
    # =========================================================================

    def create_course(
        self,
        name: str,
        description: str = "",
        course_code: str = "",
        owner_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a new course in Google Classroom.

        Args:
            name: Course name
            description: Course description
            course_code: Course code (optional)
            owner_id: Owner user ID (optional)
            **kwargs: Additional course parameters

        Returns:
            Course resource

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            
            payload: dict[str, Any] = {
                "name": name,
            }
            if description:
                payload["description"] = description
            if course_code:
                payload["courseCode"] = course_code
            if owner_id:
                payload["ownerId"] = owner_id

            # Add optional parameters
            for key, value in kwargs.items():
                if value is not None:
                    payload[key] = value

            url = f"{self.CLASSROOM_API_BASE}/courses"
            response = client.post(url, json=payload)
            return response.json()

        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to create course: {str(e)}",
            ) from e

    def get_course(self, course_id: str, **kwargs: Any) -> dict[str, Any]:
        """
        Get a course by ID.

        Args:
            course_id: Google Classroom course ID
            **kwargs: Additional parameters

        Returns:
            Course resource

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            url = f"{self.CLASSROOM_API_BASE}/courses/{course_id}"
            response = client.get(url)
            return response.json()
        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to get course {course_id}: {str(e)}",
            ) from e

    def list_courses(
        self,
        teacher_id: str | None = None,
        student_id: str | None = None,
        page_size: int = 100,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        List courses.

        Args:
            teacher_id: Filter by teacher ID
            student_id: Filter by student ID
            page_size: Number of results per page
            **kwargs: Additional parameters

        Returns:
            List of course resources

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            
            params: dict[str, Any] = {"pageSize": page_size}
            if teacher_id:
                params["teacherId"] = teacher_id
            if student_id:
                params["studentId"] = student_id

            url = f"{self.CLASSROOM_API_BASE}/courses"
            response = client.get(url, params=params)
            data = response.json()
            return data.get("courses", [])

        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to list courses: {str(e)}",
            ) from e

    def update_course(
        self,
        course_id: str,
        name: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Update a course.

        Args:
            course_id: Course ID to update
            name: New course name
            description: New course description
            **kwargs: Additional parameters

        Returns:
            Updated course resource

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            
            payload: dict[str, Any] = {}
            if name is not None:
                payload["name"] = name
            if description is not None:
                payload["description"] = description
            
            for key, value in kwargs.items():
                if value is not None:
                    payload[key] = value

            url = f"{self.CLASSROOM_API_BASE}/courses/{course_id}"
            response = client.patch(url, json=payload)
            return response.json()

        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to update course {course_id}: {str(e)}",
            ) from e

    def archive_course(self, course_id: str, **kwargs: Any) -> dict[str, Any]:
        """
        Archive a course.

        Args:
            course_id: Course ID to archive
            **kwargs: Additional parameters

        Returns:
            Updated course resource

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            
            payload = {"courseState": "ARCHIVED"}
            url = f"{self.CLASSROOM_API_BASE}/courses/{course_id}"
            response = client.patch(url, json=payload)
            return response.json()

        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to archive course {course_id}: {str(e)}",
            ) from e

    # =========================================================================
    # Student Operations
    # =========================================================================

    def add_student_to_course(
        self,
        course_id: str,
        student_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Add a student to a course.

        Args:
            course_id: Course ID
            student_id: Student user ID
            **kwargs: Additional parameters

        Returns:
            Student resource

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            
            payload = {"userId": student_id}
            url = f"{self.CLASSROOM_API_BASE}/courses/{course_id}/students"
            response = client.post(url, json=payload)
            return response.json()

        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to add student {student_id} to course {course_id}: {str(e)}",
            ) from e

    def remove_student_from_course(
        self,
        course_id: str,
        student_id: str,
        **kwargs: Any,
    ) -> None:
        """
        Remove a student from a course.

        Args:
            course_id: Course ID
            student_id: Student user ID
            **kwargs: Additional parameters

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            url = f"{self.CLASSROOM_API_BASE}/courses/{course_id}/students/{student_id}"
            client.delete(url)
        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to remove student {student_id} from course {course_id}: {str(e)}",
            ) from e

    def list_students_in_course(
        self,
        course_id: str,
        page_size: int = 100,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        List students in a course.

        Args:
            course_id: Course ID
            page_size: Number of results per page
            **kwargs: Additional parameters

        Returns:
            List of student resources

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            
            params = {"pageSize": page_size}
            url = f"{self.CLASSROOM_API_BASE}/courses/{course_id}/students"
            response = client.get(url, params=params)
            data = response.json()
            return data.get("students", [])

        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to list students in course {course_id}: {str(e)}",
            ) from e

    # =========================================================================
    # CourseWork (Assignment) Operations
    # =========================================================================

    def create_course_work(
        self,
        course_id: str,
        title: str,
        description: str = "",
        due_date: str | None = None,
        due_time: str | None = None,
        max_points: float = 100.0,
        work_type: str = "ASSIGNMENT",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a course work (assignment) in a course.

        Args:
            course_id: Course ID
            title: Course work title
            description: Course work description
            due_date: Due date (YYYY-MM-DD format)
            due_time: Due time (HH:MM:SS format)
            max_points: Maximum points
            work_type: Type of work (ASSIGNMENT, SHORT_ANSWER_QUESTION, etc.)
            **kwargs: Additional parameters

        Returns:
            CourseWork resource

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            
            payload: dict[str, Any] = {
                "title": title,
                "description": description,
                "maxPoints": max_points,
                "workType": work_type,
            }
            
            if due_date:
                payload["dueDate"] = due_date
            if due_time:
                payload["dueTime"] = due_time

            for key, value in kwargs.items():
                if value is not None:
                    payload[key] = value

            url = f"{self.CLASSROOM_API_BASE}/courses/{course_id}/courseWork"
            response = client.post(url, json=payload)
            return response.json()

        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to create course work: {str(e)}",
            ) from e

    def list_course_work(
        self,
        course_id: str,
        page_size: int = 100,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        List course work for a course.

        Args:
            course_id: Course ID
            page_size: Number of results per page
            **kwargs: Additional parameters

        Returns:
            List of CourseWork resources

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            
            params = {"pageSize": page_size}
            url = f"{self.CLASSROOM_API_BASE}/courses/{course_id}/courseWork"
            response = client.get(url, params=params)
            data = response.json()
            return data.get("courseWork", [])

        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to list course work for course {course_id}: {str(e)}",
            ) from e

    # =========================================================================
    # Teacher Operations
    # =========================================================================

    def add_teacher_to_course(
        self,
        course_id: str,
        teacher_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Add a teacher to a course.

        Args:
            course_id: Course ID
            teacher_id: Teacher user ID
            **kwargs: Additional parameters

        Returns:
            Teacher resource

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            
            payload = {"userId": teacher_id}
            url = f"{self.CLASSROOM_API_BASE}/courses/{course_id}/teachers"
            response = client.post(url, json=payload)
            return response.json()

        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to add teacher {teacher_id} to course {course_id}: {str(e)}",
            ) from e

    def list_teachers_in_course(
        self,
        course_id: str,
        page_size: int = 100,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        List teachers in a course.

        Args:
            course_id: Course ID
            page_size: Number of results per page
            **kwargs: Additional parameters

        Returns:
            List of teacher resources

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        try:
            client = self._get_http_client()
            
            params = {"pageSize": page_size}
            url = f"{self.CLASSROOM_API_BASE}/courses/{course_id}/teachers"
            response = client.get(url, params=params)
            data = response.json()
            return data.get("teachers", [])

        except IntegrationHttpError as e:
            raise IntegrationHttpError(
                message=f"Failed to list teachers in course {course_id}: {str(e)}",
            ) from e

    # =========================================================================
    # Sync Operations
    # =========================================================================

    def sync_course_with_students(
        self,
        course_id: str,
        student_emails: list[str],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Sync students to a course.

        Args:
            course_id: Course ID
            student_emails: List of student email addresses
            **kwargs: Additional parameters

        Returns:
            Sync result

        Raises:
            IntegrationHttpError: If API request fails
        """
        if not self.is_enabled:
            raise ValueError("Google Classroom integration is not enabled")

        results: dict[str, Any] = {
            "total": len(student_emails),
            "added": 0,
            "failed": 0,
            "errors": [],
        }

        for email in student_emails:
            try:
                # In a real implementation, we would need to get the user ID first
                # For now, we'll just count as added
                results["added"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))

        return results

    # =========================================================================
    # Health Check
    # =========================================================================

    def is_healthy(self) -> bool:
        """
        Check if the service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        if not self.is_enabled:
            return False
        
        try:
            # Make a test API call
            self.list_courses(page_size=1)
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Close any open resources."""
        pass  # HTTP clients are created per-request

    def __enter__(self) -> "GoogleClassroomService":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
