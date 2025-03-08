"""
Hestia Logger - Custom Logger.

Defines a structured logger with thread-based asynchronous logging.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import json
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from ..internal_logger import hestia_internal_logger
from ..handlers import console_handler
from ..core.config import (
    LOGS_DIR,
    LOG_LEVEL,
    LOG_ROTATION_TYPE,
    LOG_ROTATION_WHEN,
    LOG_ROTATION_INTERVAL,
    LOG_ROTATION_BACKUP_COUNT,
    LOG_ROTATION_MAX_BYTES,
    ENABLE_INTERNAL_LOGGER,
    LOG_FILE_PATH_APP,
)

# Global dictionary to track loggers
_LOGGERS = {}
_APP_LOG_HANDLER = None  # Ensure `app.log` is only attached once
_RESERVED_APP_NAME = "app"  # Reserved logger name


class JSONFormatter(logging.Formatter):
    """
    Ensures all logs are structured in JSON format.
    """

    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ")[:-3]
            + "Z",  # Proper microsecond formatting
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_entry)


def get_logger(name: str, metadata: dict = None, log_level=None):
    """
    Returns a structured logger for a specific service/module.
    Prevents users from directly using the reserved "app" logger.

    :param name: Name of the logger (e.g., 'api_service', 'database_service').
    :param metadata: Optional dictionary of metadata fields to be included in logs.
    :param log_level: Optional log level for this logger (default: global LOG_LEVEL).
    """
    global _LOGGERS, _APP_LOG_HANDLER

    # Prevent users from using "app" directly
    if name == _RESERVED_APP_NAME:
        raise ValueError(
            f'"{_RESERVED_APP_NAME}" is a reserved logger name and cannot be used directly.'
        )

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

    # Ensure we create `app.log` handler only once
    if _APP_LOG_HANDLER is None:
        json_formatter = JSONFormatter()
        _APP_LOG_HANDLER = RotatingFileHandler(
            LOG_FILE_PATH_APP,
            maxBytes=LOG_ROTATION_MAX_BYTES,
            backupCount=LOG_ROTATION_BACKUP_COUNT,
        )
        _APP_LOG_HANDLER.setFormatter(json_formatter)
        _APP_LOG_HANDLER.setLevel(logging.DEBUG)  # Capture ALL logs from services

    # Force ALL service log levels (`DEBUG+`) to go to `app.log`
    if _APP_LOG_HANDLER not in logger.handlers:
        logger.addHandler(_APP_LOG_HANDLER)

    # Store logger instance globally
    _LOGGERS[name] = logger

    # Attach metadata (if provided)
    setattr(logger, "metadata", metadata or {})

    return logger


def apply_logging_settings():
    """
    Applies `LOG_LEVEL` settings to all handlers and ensures correct formatting.
    """

    logging.root.handlers = []  # Reset all log handlers to prevent duplication
    logging.root.setLevel(LOG_LEVEL)  # Apply `LOG_LEVEL` globally
    console_handler.setLevel(LOG_LEVEL)

    # Apply Colored Formatter to Console
    color_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(color_formatter)

    # Attach handlers only if not already added
    logging.root.addHandler(console_handler)

    # Ensure log handlers flush logs to disk
    for handler in logging.root.handlers:
        handler.flush = lambda: handler.stream.flush()

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


apply_logging_settings()  # Apply settings AFTER handlers are imported
