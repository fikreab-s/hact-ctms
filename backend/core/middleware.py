"""
Core — Audit Middleware (Thread-Local Request Context)
========================================================
Captures the current request's user, IP address, and user agent
into thread-local storage so that Django signals and model save()
methods can access them without requiring the request object.

21 CFR Part 11 compliance: Every data modification must record WHO
made the change and FROM WHERE.
"""

import threading
import logging

logger = logging.getLogger("hact_ctms.audit")

_thread_locals = threading.local()


def get_current_request():
    """Return the current request from thread-local storage."""
    return getattr(_thread_locals, "request", None)


def get_current_user():
    """Return the current authenticated user, or None."""
    request = get_current_request()
    if request and hasattr(request, "user") and request.user.is_authenticated:
        return request.user
    return None


def get_client_ip(request=None):
    """Extract client IP from the request, handling proxies (X-Forwarded-For)."""
    request = request or get_current_request()
    if not request:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request=None):
    """Extract user agent string from the request."""
    request = request or get_current_request()
    if not request:
        return ""
    return request.META.get("HTTP_USER_AGENT", "")


class AuditMiddleware:
    """Middleware that stores the current request in thread-local storage.

    This allows audit signals and model save methods to access request
    context (user, IP, user agent) without explicit passing.

    Must be placed AFTER AuthenticationMiddleware in MIDDLEWARE list.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        try:
            response = self.get_response(request)
        finally:
            # Clean up to prevent memory leaks between requests
            if hasattr(_thread_locals, "request"):
                del _thread_locals.request
        return response
