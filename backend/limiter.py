"""
JobShield AI — Centralized Rate Limiter

Exports a shared SlowAPI Limiter instance with graceful fallback
if slowapi is not installed.
"""

import logging

logger = logging.getLogger("jobshield.limiter")

class DummyLimiter:
    """Fallback no-op limiter when slowapi is not installed or disabled."""
    def limit(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator


try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
except ImportError:
    limiter = DummyLimiter()
    logger.warning("slowapi not installed — rate limiting disabled.")
