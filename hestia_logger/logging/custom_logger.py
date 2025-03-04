"""
Custom Logger Setup.

Features:
- Provides a `LoggerManager` class to manage logging configurations and handlers.
- Supports logging to files (`logs/app.log`, `logs/all.log` for local, `/var/logs/app.log` for containers).
- Adds Elasticsearch integration **only if** `ELASTICSEARCH_HOST` is set.
- Suppresses noisy logs from third-party libraries like FastAPI, Uvicorn, and Beanie.
- Ensures structured, readable, and organized logging for application and external logs.
- Supports both structured JSON (`app.log` for ELK) and human-readable text logs (`all.log`).

Environment Variables:
- ENVIRONMENT: `local` (default) or `container` (changes log directory to `/var/logs`).
- LOG_LEVEL: Must be explicitly set (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- LOG_FORMAT: `JSON` (default) or `TEXT` for structured vs human-readable logs.
- ELASTICSEARCH_HOST: (Optional) Elasticsearch endpoint for log forwarding.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
import coloredlogs
from .handlers import console_handler, file_handler_app, file_handler_all
from .config import HOSTNAME, CONTAINER_ID


def get_logger(name: str) -> logging.Logger:
    """
    Fetches and returns a logger with the specified name, configured
    according to the app's logging settings.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler_app)
        logger.addHandler(file_handler_all)

    return logger


# Apply colored logs to the console handler for better readability
coloredlogs.install(
    level="INFO",
    logger=get_logger("app_logger"),
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def add_extra_log_attributes(record_factory):
    """
    Wraps the log record factory to add hostname and container ID to each log record.

    Args:
        record_factory (callable): The original log record factory function.

    Returns:
        callable: Wrapped log record factory.
    """

    def wrapper(name, level, fn, lno, msg, args, exc_info, func=None, sinfo=None):
        record = record_factory(name, level, fn, lno, msg, args, exc_info, func, sinfo)
        record.hostname = HOSTNAME
        record.container_id = CONTAINER_ID
        return record

    return wrapper


# Attach extra log attributes globally
logging.setLogRecordFactory(add_extra_log_attributes(logging.getLogRecordFactory()))

# Suppress noisy logs from third-party libraries
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
logging.getLogger("beanie").setLevel(logging.ERROR)
