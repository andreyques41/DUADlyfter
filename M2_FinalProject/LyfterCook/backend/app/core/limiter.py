"""Rate limiting extension.

This module exposes a shared Flask-Limiter instance so route modules can
decorate endpoints with per-route limits.
"""

import os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import settings


def _storage_uri() -> str:
    """Return the limiter storage backend URI.

    Defaults to in-memory storage for development to avoid requiring Redis.
    Production can override using RATELIMIT_STORAGE_URI (recommended: Redis).
    """
    explicit = os.getenv("RATELIMIT_STORAGE_URI")
    if explicit:
        return explicit

    if getattr(settings, "FLASK_ENV", "development") == "production":
        return settings.get_redis_url()

    return "memory://"


def _enabled() -> bool:
    """Enable rate limiting except during tests."""
    if os.getenv("TESTING", "False").lower() == "true":
        return False
    if getattr(settings, "FLASK_ENV", "development") == "testing":
        return False
    return True


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri(),
    default_limits=[],
    enabled=_enabled(),
)
