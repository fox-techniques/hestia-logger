"""
Hestia Logger - Custom Logger.

Defines a structured logger with thread-based asynchronous logging.
"""

import socket
import os
import json
import threading
import uuid
from datetime import datetime
import logging
import colorlog
from ..internal_logger import hestia_internal_logger
from ..handlers import console_handler, file_handler_app, file_handler_all, es_handler
from ..core.config import LOG_LEVEL, ENABLE_INTERNAL_LOGGER

__all__ = ["get_logger"]


class JSONFormatter(logging.Formatter):
    """
    Custom JSON log formatter for ELK.
    Ensures application name and metadata are dynamically included.
    """

    def format(self, record):
        """
        Converts a log record into a structured JSON format.
        """
        application_name = getattr(record, "application_name", "unknown-app")
        metadata = getattr(record, "metadata", {})

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "hostname": socket.gethostname(),
            "container_id": (
                open("/proc/self/cgroup").read().splitlines()[-1].split("/")[-1]
                if os.path.exists("/proc/self/cgroup")
                else "N/A"
            ),
            "application": application_name,
            "event": record.getMessage(),
            "thread": threading.get_ident(),
            "process": os.getpid(),
            "uuid": str(uuid.uuid4()),
            "metadata": metadata,
        }
        return json.dumps(log_entry)


def apply_logging_settings():
    """
    Applies LOG_LEVEL settings to all handlers and ensures correct formatting.
    """

    # Reset all log handlers to prevent duplication
    logging.root.handlers = []

    # Apply LOG_LEVEL Globally
    logging.root.setLevel(LOG_LEVEL)

    # Ensure All Handlers Respect LOG_LEVEL
    console_handler.setLevel(LOG_LEVEL)
    file_handler_app.setLevel(LOG_LEVEL)
    file_handler_all.setLevel(LOG_LEVEL)

    # Define Formatters (JSON for `app.log`, Text for `all.log`)
    json_formatter = JSONFormatter()  # Now using the correct JSON formatter
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

    # Attach handlers only if not already added
    logging.root.addHandler(console_handler)
    logging.root.addHandler(file_handler_app)
    logging.root.addHandler(file_handler_all)

    # Ensure Internal Logger Respects LOG_LEVEL
    if hasattr(hestia_internal_logger, "setLevel"):
        hestia_internal_logger.setLevel(LOG_LEVEL)

    # Ensure Internal Logger Is Enabled or Disabled Properly
    if hasattr(hestia_internal_logger, "disabled"):
        hestia_internal_logger.disabled = not ENABLE_INTERNAL_LOGGER

    # Log final settings (Only if INFO or lower)
    if hasattr(hestia_internal_logger, "info") and LOG_LEVEL <= logging.INFO:
        hestia_internal_logger.info(f"Applied LOG_LEVEL: {LOG_LEVEL}")
        hestia_internal_logger.info(f"ENABLE_INTERNAL_LOGGER: {ENABLE_INTERNAL_LOGGER}")


apply_logging_settings()  # Now it runs AFTER handlers are imported


def get_logger(name: str, metadata: dict = None):
    """
    Returns a structured logger with async logging enabled.

    :param name: The application or service name to be used in logs.
    :param metadata: Optional dictionary of metadata fields to be included in logs.
    """
    hestia_internal_logger.info(f"🔍 Applying LOG_LEVEL in get_logger(): {LOG_LEVEL}")

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

    # Store the application name & metadata dynamically
    setattr(python_logger, "application_name", name)
    setattr(python_logger, "metadata", metadata or {})

    return python_logger
