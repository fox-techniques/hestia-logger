"""
Hestia Logger - Custom Logger.

Defines a structured logger with thread-based asynchronous logging.
"""

import structlog
import logging
import colorlog
from structlog.processors import TimeStamper, JSONRenderer
from structlog.contextvars import merge_contextvars
from ..internal_logger import hestia_internal_logger
from ..handlers import console_handler, file_handler_app, file_handler_all, es_handler
from ..core.config import LOG_LEVEL, ENABLE_INTERNAL_LOGGER

__all__ = ["get_logger"]


def apply_logging_settings():
    """
    Applies LOG_LEVEL settings to all handlers and ensures correct formatting.
    """

    # Apply LOG_LEVEL Globally
    logging.root.setLevel(LOG_LEVEL)

    # Ensure All Handlers Respect LOG_LEVEL
    for handler in logging.root.handlers:
        handler.setLevel(LOG_LEVEL)

    console_handler.setLevel(LOG_LEVEL)
    file_handler_app.setLevel(LOG_LEVEL)
    file_handler_all.setLevel(LOG_LEVEL)

    # Define Formatters (JSON for `app.log`, Text for `all.log`)
    json_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    )
    text_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Apply JSON to `app.log`
    file_handler_app.setFormatter(json_formatter)

    # Apply Human-Readable Format to `all.log`
    file_handler_all.setFormatter(text_formatter)

    # Apply Colored Formatter to Console
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    console_handler.setFormatter(color_formatter)

    # Ensure Internal Logger Is Enabled or Disabled Properly
    if hasattr(hestia_internal_logger, "disabled"):
        hestia_internal_logger.disabled = not ENABLE_INTERNAL_LOGGER

    # Log final settings
    if hasattr(
        hestia_internal_logger, "info"
    ):  # Prevent crashes when logger is disabled
        hestia_internal_logger.info(f"Applied LOG_LEVEL: {LOG_LEVEL}")
        hestia_internal_logger.info(f"ENABLE_INTERNAL_LOGGER: {ENABLE_INTERNAL_LOGGER}")


apply_logging_settings()  # Now it runs AFTER handlers are imported


def get_logger(name: str):
    """
    Returns a structured logger with thread-based asynchronous logging.
    """
    if hasattr(hestia_internal_logger, "info"):
        hestia_internal_logger.info(
            f"🔍 Applying LOG_LEVEL in get_logger(): {LOG_LEVEL}"
        )

    python_logger = logging.getLogger(name)
    python_logger.setLevel(LOG_LEVEL)
    python_logger.propagate = False

    # Attach handlers if not already attached
    if not python_logger.hasHandlers():
        python_logger.addHandler(console_handler)
        python_logger.addHandler(file_handler_app)
        python_logger.addHandler(file_handler_all)

        if hasattr(hestia_internal_logger, "info"):
            for handler in python_logger.handlers:
                hestia_internal_logger.info(
                    f"Attached Handler: {handler} (Level: {handler.level} - {logging.getLevelName(handler.level)})"
                )

    return python_logger
