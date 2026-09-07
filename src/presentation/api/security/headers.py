from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


HSTS_VALUE = "max-age=63072000; includeSubDomains; preload"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Ajoute les en-tetes de securite recommandes pour une API JSON."""

    def __init__(self, app, enable_hsts: bool = False):
        super().__init__(app)
        self._enable_hsts = enable_hsts

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        headers = response.headers

        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("X-Frame-Options", "DENY")
        headers.setdefault(
            "Referrer-Policy",
            "no-referrer",
        )
        if not headers.get("content-type", "").startswith("text/html"):
            headers.setdefault(
                "Content-Security-Policy",
                "default-src 'none'; frame-ancestors 'none'",
            )
        headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )
        headers.setdefault("Cache-Control", "no-store")

        if self._enable_hsts:
            headers.setdefault(
                "Strict-Transport-Security",
                HSTS_VALUE,
            )

        return response
