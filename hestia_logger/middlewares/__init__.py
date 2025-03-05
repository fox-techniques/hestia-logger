"""
Middlewares Module Initialization.

This module provides structured logging middleware for FastAPI applications.

Features:
- Initializes async request logging middleware.
- Ensures all HTTP requests and responses are logged.
- Provides an import interface for middleware integration.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

from .middleware import AsyncLoggingMiddleware

__all__ = [
    "AsyncLoggingMiddleware",
]
