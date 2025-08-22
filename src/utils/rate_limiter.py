"""Simple rate limiting utility for API endpoints."""

import time
from collections import defaultdict, deque
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import HTTPException, status


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window approach.

    This implementation tracks request timestamps per client/endpoint
    and enforces rate limits based on configurable windows.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store request timestamps per client key
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, client_key: str) -> bool:
        """
        Check if request is allowed for client.

        Args:
            client_key: Unique identifier for client (IP, session, etc.)

        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        client_requests = self.requests[client_key]

        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()

        # Check if under limit
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            return True

        return False

    def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """
        Clean up old client entries to prevent memory leaks.

        Args:
            max_age_seconds: Remove client entries older than this
        """
        now = time.time()
        cutoff = now - max_age_seconds

        keys_to_remove = []
        for client_key, requests in self.requests.items():
            if not requests or requests[-1] < cutoff:
                keys_to_remove.append(client_key)

        for key in keys_to_remove:
            del self.requests[key]


# Global rate limiter instances for different endpoint types
openai_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)  # 5 requests per minute
assessment_rate_limiter = RateLimiter(
    max_requests=20, window_seconds=300
)  # 20 requests per 5 minutes


def rate_limit_openai(get_client_key: Callable[..., str] = lambda: "default"):
    """
    Decorator to rate limit OpenAI API calls.

    Args:
        get_client_key: Function to extract client identifier from request
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client_key = get_client_key(*args, **kwargs)

            if not openai_rate_limiter.is_allowed(client_key):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded for OpenAI API calls. Please try again later.",
                    headers={"Retry-After": "60"},
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def rate_limit_assessment(get_client_key: Callable[..., str] = lambda: "default"):
    """
    Decorator to rate limit assessment endpoints.

    Args:
        get_client_key: Function to extract client identifier from request
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client_key = get_client_key(*args, **kwargs)

            if not assessment_rate_limiter.is_allowed(client_key):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded for assessment endpoints. Please try again later.",
                    headers={"Retry-After": "300"},
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
