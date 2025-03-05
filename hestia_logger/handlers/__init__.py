"""
Handlers Module Initialization.

This module provides structured logging handlers.

Features:
- Supports console logging.
- Implements file-based rotating log handlers.
- Adds asynchronous Elasticsearch logging (if configured).

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

from .console_handler import console_handler
from .file_handler import file_handler_app, file_handler_all
from .elasticsearch_handler import es_handler

__all__ = [
    "console_handler",
    "file_handler_app",
    "file_handler_all",
    "es_handler",
]
