"""
Hestia Logger Package Initialization.

This module initializes all logging components for async logging.

Features:
- Provides structured logging with `structlog`.
- Ensures all log handlers (console, file, Elasticsearch) are set up.
- Exposes logging middleware for FastAPI applications.
- Centralized entry point for logging utilities.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

from .core import get_logger, LOG_LEVEL, LOG_FORMAT, ELASTICSEARCH_HOST
from .handlers import console_handler, file_handler_app, file_handler_all, es_handler
from .middlewares import AsyncLoggingMiddleware
from .utils import async_http_request, enable_request_logging
from .decorators import _log_execution

__all__ = [
    "get_logger",
    "LOG_LEVEL",
    "LOG_FORMAT",
    "ELASTICSEARCH_HOST",
    "console_handler",
    "file_handler_app",
    "file_handler_all",
    "es_handler",
    "AsyncLoggingMiddleware",
    "async_http_request",
    "enable_request_logging",
    "_log_execution",
]
