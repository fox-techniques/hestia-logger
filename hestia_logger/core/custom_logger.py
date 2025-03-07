"""
Hestia Logger - Custom Logger.

Defines a structured logger with thread-based asynchronous logging.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
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
from ..handlers import console_handler, file_handler_app
from ..handlers.file_handler import ThreadedFileHandler
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from ..core.config import (
    LOGS_DIR,
    LOG_LEVEL,
    LOG_FILE_PATH_APP,
    LOG_ROTATION_TYPE,
    LOG_ROTATION_WHEN,
    LOG_ROTATION_INTERVAL,
    LOG_ROTATION_BACKUP_COUNT,
    LOG_ROTATION_MAX_BYTES,
    ENABLE_INTERNAL_LOGGER,
)

# Global dictionary to track loggers
_LOGGERS = {}


def get_logger(name: str, metadata: dict = None, log_level=None):
    """
    Returns a structured logger for a specific service/module.

    :param name: Name of the logger (e.g., 'api_service', 'database_service').
    :param metadata: Optional dictionary of metadata fields to be included in logs.
    :param log_level: Optional log level for this logger (default: global LOG_LEVEL).
    """
    global _LOGGERS

    if name in _LOGGERS:
        return _LOGGERS[name]  # Return existing logger if already created

    log_level = log_level or LOG_LEVEL
    service_log_file = os.path.join(LOGS_DIR, f"{name}.log")

    # Choose log rotation type for per-service logs
    if LOG_ROTATION_TYPE == "time":
        service_handler = TimedRotatingFileHandler(
            service_log_file,
            when=LOG_ROTATION_WHEN,
            interval=LOG_ROTATION_INTERVAL,
            backupCount=LOG_ROTATION_BACKUP_COUNT,
        )
    else:
        service_handler = RotatingFileHandler(
            service_log_file,
            maxBytes=LOG_ROTATION_MAX_BYTES,
            backupCount=LOG_ROTATION_BACKUP_COUNT,
        )

    # Per-service logs (text format)
    service_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    service_handler.setLevel(log_level)

    # Create logger instance
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False  # Prevent root logger duplication

    # Attach handlers for service logs
    logger.addHandler(console_handler)  # Console logging
    logger.addHandler(service_handler)  # Per-service file logging (text format)

    # If this is the "app" logger, attach only the JSON formatter
    if name == "app":
        app_log_handler = RotatingFileHandler(
            LOG_FILE_PATH_APP,
            maxBytes=LOG_ROTATION_MAX_BYTES,
            backupCount=LOG_ROTATION_BACKUP_COUNT,
        )
        app_log_handler.setFormatter(
            logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "%(name)s", "message": "%(message)s"}'
            )
        )
        app_log_handler.setLevel(logging.INFO)  # Only log important messages

        # Remove any previously attached handlers to avoid duplication
        logger.handlers = [app_log_handler]  # Only attach JSON formatter for `app.log`

    # Store logger instance globally
    _LOGGERS[name] = logger

    # Attach metadata (if provided)
    setattr(logger, "metadata", metadata or {})

    return logger


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

    # Define Formatters (JSON for `app.log`, Text for service logs)
    json_formatter = JSONFormatter()  # JSON formatting for structured logging
    text_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Apply JSON formatter to `app.log`
    file_handler_app.setFormatter(json_formatter)

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
