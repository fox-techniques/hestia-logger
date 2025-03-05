"""
Decorators Module Initialization.

This module provides structured logging decorators for:
- Function execution logging (sync & async).
- Automatic masking of sensitive arguments.
- Non-blocking logging for FastAPI and async applications.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

from .decorators import _log_execution

__all__ = [
    "_log_execution",
]
