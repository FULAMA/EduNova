"""
Integration HTTP Client.

A shared HTTP client for making requests to external integration APIs.
Provides:
- Timeout configuration
- Retry logic with exponential backoff
- Error handling
- Request/response logging
- Rate limiting support
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class IntegrationHttpError(Exception):
    """Custom exception for HTTP errors in integrations."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: httpx.Response | None = None,
        request: httpx.Request | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
        self.request = request

    def __str__(self) -> str:
        parts = [f"IntegrationHttpError: {self.message}"]
        if self.status_code:
            parts.append(f"(status_code={self.status_code})")
        return " ".join(parts)


@dataclass
class IntegrationHttpConfig:
    """Configuration for the HTTP client."""

    base_url: str | None = None
    timeout: float = 30.0  # seconds
    max_retries: int = 3
    retry_delay: float = 1.0  # base delay in seconds
    max_retry_delay: float = 10.0  # maximum delay in seconds
    retry_codes: set[int] = field(default_factory=lambda: {429, 500, 502, 503, 504})
    headers: dict[str, str] = field(default_factory=dict)
    auth: httpx.Auth | None = None
    
    def with_auth(self, auth: httpx.Auth) -> "IntegrationHttpConfig":
        """Create a new config with authentication."""
        return IntegrationHttpConfig(
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            max_retry_delay=self.max_retry_delay,
            retry_codes=self.retry_codes,
            headers=self.headers,
            auth=auth,
        )


class IntegrationHttpClient:
    """
    HTTP client for external integrations.
    
    Features:
    - Automatic retries with exponential backoff
    - Timeout handling
    - Custom error types
    - Request/response logging
    - Support for both sync and async operations
    """

    def __init__(self, config: IntegrationHttpConfig | None = None) -> None:
        """
        Initialize the HTTP client.
        
        Args:
            config: HTTP client configuration
        """
        self.config = config or IntegrationHttpConfig()
        self._sync_client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

    @property
    def sync_client(self) -> httpx.Client:
        """Get or create synchronous client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=self.config.base_url or '',
                timeout=self.config.timeout,
                headers=self.config.headers,
                auth=self.config.auth,
            )
        return self._sync_client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create asynchronous client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.config.base_url or '',
                timeout=self.config.timeout,
                headers=self.config.headers,
                auth=self.config.auth,
            )
        return self._async_client

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff."""
        delay = self.config.retry_delay * (2 ** (attempt - 1))
        return min(delay, self.config.max_retry_delay)

    def _should_retry(self, status_code: int) -> bool:
        """Check if a status code should trigger a retry."""
        return status_code in self.config.retry_codes

    def _log_request(self, method: str, url: str, headers: dict[str, str] | None = None) -> None:
        """Log request details (without sensitive data)."""
        safe_headers = {k: v for k, v in (headers or {}).items() if k.lower() not in ('authorization', 'api-key')}
        logger.debug(f"[HTTP] {method} {url} - Headers: {list(safe_headers.keys())}")

    def _log_response(self, response: httpx.Response) -> None:
        """Log response details."""
        logger.debug(f"[HTTP] {response.status_code} {response.url} - {len(response.content)} bytes")

    def _raise_for_status(self, response: httpx.Response, context: str = "") -> None:
        """Raise IntegrationHttpError for non-2xx status codes."""
        if 200 <= response.status_code < 300:
            return
        
        try:
            error_data = response.json()
        except (json.JSONDecodeError, ValueError):
            error_data = None
        
        message = f"{context}: HTTP {response.status_code}"
        if error_data and isinstance(error_data, dict):
            error_msg = error_data.get("message") or error_data.get("error") or str(error_data)
            if error_msg:
                message = f"{message} - {error_msg}"
        
        raise IntegrationHttpError(
            message=message,
            status_code=response.status_code,
            response=response,
        )

    # =========================================================================
    # Synchronous Methods
    # =========================================================================

    def get(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send a synchronous GET request."""
        return self._request("GET", url, **kwargs)

    def post(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send a synchronous POST request."""
        return self._request("POST", url, **kwargs)

    def put(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send a synchronous PUT request."""
        return self._request("PUT", url, **kwargs)

    def patch(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send a synchronous PATCH request."""
        return self._request("PATCH", url, **kwargs)

    def delete(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send a synchronous DELETE request."""
        return self._request("DELETE", url, **kwargs)

    def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send a synchronous HTTP request with retry logic."""
        last_exception: Exception | None = None
        
        for attempt in range(1, self.config.max_retries + 1):
            try:
                # Build full URL if base_url is set
                if self.config.base_url and not url.startswith(("http://", "https://")):
                    full_url = f"{self.config.base_url.rstrip('/')}/{url.lstrip('/')}"
                else:
                    full_url = url
                
                # Prepare request
                headers = {**self.config.headers, **kwargs.get("headers", {})}
                self._log_request(method, full_url, headers)
                
                # Send request
                response = self.sync_client.request(method, full_url, **kwargs)
                self._log_response(response)
                
                # Check if we should retry
                if self._should_retry(response.status_code):
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"[HTTP] Retry {attempt}/{self.config.max_retries} - Waiting {delay:.1f}s")
                    time.sleep(delay)
                    continue
                
                # Raise for non-2xx status codes
                self._raise_for_status(response, f"{method} {full_url}")
                return response
                
            except httpx.TimeoutException as e:
                last_exception = IntegrationHttpError(
                    message=f"Request timed out: {method} {url}",
                    status_code=None,
                )
                if attempt < self.config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"[HTTP] Timeout retry {attempt}/{self.config.max_retries} - Waiting {delay:.1f}s")
                    time.sleep(delay)
                else:
                    raise last_exception from e
                    
            except httpx.RequestError as e:
                last_exception = IntegrationHttpError(
                    message=f"Request failed: {method} {url} - {str(e)}",
                    status_code=None,
                )
                if attempt < self.config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"[HTTP] Error retry {attempt}/{self.config.max_retries} - Waiting {delay:.1f}s")
                    time.sleep(delay)
                else:
                    raise last_exception from e
        
        # This should not be reached, but just in case
        if last_exception:
            raise last_exception
        raise IntegrationHttpError(message=f"Request failed after {self.config.max_retries} retries")

    # =========================================================================
    # Asynchronous Methods
    # =========================================================================

    async def get_async(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send an asynchronous GET request."""
        return await self._request_async("GET", url, **kwargs)

    async def post_async(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send an asynchronous POST request."""
        return await self._request_async("POST", url, **kwargs)

    async def put_async(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send an asynchronous PUT request."""
        return await self._request_async("PUT", url, **kwargs)

    async def patch_async(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send an asynchronous PATCH request."""
        return await self._request_async("PATCH", url, **kwargs)

    async def delete_async(
        self,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send an asynchronous DELETE request."""
        return await self._request_async("DELETE", url, **kwargs)

    async def _request_async(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send an asynchronous HTTP request with retry logic."""
        last_exception: Exception | None = None
        
        for attempt in range(1, self.config.max_retries + 1):
            try:
                # Build full URL if base_url is set
                if self.config.base_url and not url.startswith(("http://", "https://")):
                    full_url = f"{self.config.base_url.rstrip('/')}/{url.lstrip('/')}"
                else:
                    full_url = url
                
                # Prepare request
                headers = {**self.config.headers, **kwargs.get("headers", {})}
                self._log_request(method, full_url, headers)
                
                # Send request
                response = await self.async_client.request(method, full_url, **kwargs)
                self._log_response(response)
                
                # Check if we should retry
                if self._should_retry(response.status_code):
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"[HTTP] Async retry {attempt}/{self.config.max_retries} - Waiting {delay:.1f}s")
                    await asyncio.sleep(delay)
                    continue
                
                # Raise for non-2xx status codes
                self._raise_for_status(response, f"{method} {full_url}")
                return response
                
            except httpx.TimeoutException as e:
                last_exception = IntegrationHttpError(
                    message=f"Request timed out: {method} {url}",
                    status_code=None,
                )
                if attempt < self.config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"[HTTP] Async timeout retry {attempt}/{self.config.max_retries} - Waiting {delay:.1f}s")
                    await asyncio.sleep(delay)
                else:
                    raise last_exception from e
                    
            except httpx.RequestError as e:
                last_exception = IntegrationHttpError(
                    message=f"Request failed: {method} {url} - {str(e)}",
                    status_code=None,
                )
                if attempt < self.config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"[HTTP] Async error retry {attempt}/{self.config.max_retries} - Waiting {delay:.1f}s")
                    await asyncio.sleep(delay)
                else:
                    raise last_exception from e
        
        # This should not be reached
        if last_exception:
            raise last_exception
        raise IntegrationHttpError(message=f"Request failed after {self.config.max_retries} retries")

    def close(self) -> None:
        """Close both sync and async clients."""
        if self._sync_client:
            self._sync_client.close()
        if self._async_client:
            pass

    async def aclose(self) -> None:
        """Close async client."""
        if self._async_client:
            await self._async_client.aclose()

    def __enter__(self) -> "IntegrationHttpClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    async def __aenter__(self) -> "IntegrationHttpClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()
