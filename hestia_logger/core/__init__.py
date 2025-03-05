"""
Core Module Initialization.

This module sets up the async logging system and exposes core logging utilities.

Features:
- Initializes async logging with `structlog`.
- Ensures log handlers (console, file, Elasticsearch) are attached.
- Provides a simple import interface for the rest of the application.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

from .config import LOG_LEVEL, LOG_FORMAT, ELASTICSEARCH_HOST
from .custom_logger import get_logger

__all__ = [
    "get_logger",
    "LOG_LEVEL",
    "LOG_FORMAT",
    "ELASTICSEARCH_HOST",
]
