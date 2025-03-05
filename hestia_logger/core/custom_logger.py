"""
Custom Structured Logger.

This module provides structured logging capabilities using `structlog`.
It ensures logs are properly formatted, routed to console and file handlers,
and integrates seamlessly with the internal logging system.

Features:
- Provides structured JSON logs with contextual metadata.
- Routes logs to multiple handlers (console, file, Elasticsearch if enabled).
- Ensures logs are propagated correctly in async and sync environments.
- Supports internal debugging via `hestia_internal_logger`.

Handlers:
- `console_handler` → Logs messages to the console.
- `file_handler_app` → Logs structured JSON to `app.log`.
- `file_handler_all` → Logs all messages in human-readable format to `all.log`.
- `es_handler` (Optional) → Sends logs to Elasticsearch if configured.

Usage:
Import `get_logger(name)` to create a structured logger for use in any module.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import structlog
import logging
from structlog.processors import TimeStamper, JSONRenderer
from structlog.contextvars import merge_contextvars
from ..internal_logger import hestia_internal_logger
from ..handlers import console_handler, file_handler_app, file_handler_all, es_handler
from ..core.config import HOSTNAME, CONTAINER_ID


def get_logger(name: str):
    """
    Returns a structured logger with async logging enabled.
    """
    hestia_internal_logger.debug(f"Creating logger: {name}")

    logger = structlog.get_logger(name).bind(
        hostname=HOSTNAME, container_id=CONTAINER_ID
    )

    # Ensure handlers are properly attached
    python_logger = logging.getLogger(name)
    python_logger.setLevel(logging.DEBUG)
    python_logger.propagate = False  # Ensures logs do not bypass handlers

    # Ensure logs reach `app.log` and `all.log`
    if not python_logger.hasHandlers():
        hestia_internal_logger.debug(f"Attaching handlers to logger: {name}")
        python_logger.addHandler(console_handler)
        python_logger.addHandler(file_handler_app)  # Ensures app.log works
        python_logger.addHandler(file_handler_all)  # Ensures all.log works

        if es_handler:
            python_logger.addHandler(es_handler)

    # Manually send log records to all handlers
    def force_log_delivery(message, level=logging.DEBUG):
        record = logging.LogRecord(name, level, "", 0, message, None, None)
        for handler in python_logger.handlers:
            hestia_internal_logger.debug(f"📨 Sending log to handler: {handler}")
            handler.handle(record)

    # Test log delivery
    force_log_delivery("Testing manual log handling...", logging.INFO)

    return logger


# Configure structlog for structured logging
structlog.configure(
    processors=[
        merge_contextvars,
        TimeStamper(fmt="iso"),
        JSONRenderer(),
    ],
    context_class=dict,
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
    logger_factory=structlog.PrintLoggerFactory(),
)
