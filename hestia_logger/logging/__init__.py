"""
Initialize the logging package.

Features:
- Ensures all loggers are pre-configured and available for import.
- Loads configurations, handlers, and decorators into the logging system.
- Provides structured logging support for both JSON and plain text formats.
- Supports Elasticsearch integration for centralized logging.

Environment Variables:
- LOG_LEVEL: Must be explicitly set (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- LOG_FORMAT: `JSON` (default) or `TEXT` for structured vs human-readable logs.
- ELASTICSEARCH_HOST: (Optional) Elasticsearch endpoint for log forwarding.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

# Import and initialize logging components
from .config import LOG_LEVEL, LOG_FORMAT, ELASTICSEARCH_HOST
from .handlers import console_handler, file_handler_app, file_handler_all
from .custom_logger import get_logger, add_extra_log_attributes
from .decorators import _log_execution


__all__ = [
    "get_logger",
    "add_extra_log_attributes",
    "_log_execution",
    "console_handler",
    "file_handler_app",
    "file_handler_all",
    "LOG_LEVEL",
    "LOG_FORMAT",
    "ELASTICSEARCH_HOST",
]
