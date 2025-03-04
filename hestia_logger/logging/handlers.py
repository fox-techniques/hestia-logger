"""
Log Handlers.

Features:
- Provides modular logging handlers for console, file, and cloud-based logging.
- Supports structured JSON logging and plain text logging.
- Implements rotating file handlers to prevent excessive log growth.
- Adds Elasticsearch handler for direct ELK integration **only if ELASTICSEARCH_HOST is set**.
- Ensures application logs are structured (`app.log`), while all logs (`all.log`) remain human-readable.

Environment Variables:
- LOG_LEVEL: Must be explicitly set (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- LOG_FORMAT: `JSON` (default) or `TEXT` for structured vs human-readable logs.
- ELASTICSEARCH_HOST: (Optional) Elasticsearch endpoint for log forwarding.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from elasticsearch import Elasticsearch
from .config import (
    LOG_FILE_PATH_APP,
    LOG_FILE_PATH_ALL,
    LOG_LEVEL,
    LOG_FORMAT,
    ELASTICSEARCH_HOST,
)


# JSON log formatter
def json_log_formatter():
    """
    Returns a JSON log formatter that includes metadata such as hostname and container ID.

    Returns:
        jsonlogger.JsonFormatter: Configured JSON log formatter instance.
    """
    return jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s hostname=%(hostname)s container_id=%(container_id)s"
    )


# Log formatters
FORMATTERS = {
    "json": json_log_formatter(),
    "plain": logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
}


def get_console_handler():
    """
    Creates a console log handler with the appropriate formatter.

    Returns:
        logging.StreamHandler: Configured console handler.
    """
    handler = logging.StreamHandler()
    handler.setLevel(LOG_LEVEL)
    handler.setFormatter(
        FORMATTERS["json"] if LOG_FORMAT == "JSON" else FORMATTERS["plain"]
    )
    return handler


def get_file_handler(log_file, structured=True):
    """
    Creates a rotating file handler with the appropriate formatter.

    Args:
        log_file (str): Path to the log file.
        structured (bool): Whether to use JSON formatting (for ELK) or plain text.

    Returns:
        logging.handlers.RotatingFileHandler: Configured file handler.
    """
    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    handler.setLevel(LOG_LEVEL)
    handler.setFormatter(FORMATTERS["json"] if structured else FORMATTERS["plain"])
    return handler


# Register handlers
console_handler = get_console_handler()
file_handler_app = get_file_handler(
    LOG_FILE_PATH_APP, structured=True
)  # JSON structured logs
file_handler_all = get_file_handler(
    LOG_FILE_PATH_ALL, structured=False
)  # Human-readable logs

# Add Elasticsearch Handler if enabled
if ELASTICSEARCH_HOST:

    class ElasticsearchHandler(logging.Handler):
        """
        Custom logging handler to send logs directly to Elasticsearch.
        """

        def __init__(self, host):
            super().__init__()
            self.es = Elasticsearch([host])

        def emit(self, record):
            try:
                log_entry = self.format(record)
                self.es.index(index="application-logs", body=log_entry)
            except Exception as e:
                print(f"⚠️ Failed to send log to Elasticsearch: {e}")

    es_handler = ElasticsearchHandler(ELASTICSEARCH_HOST)
    es_handler.setLevel(LOG_LEVEL)
    es_handler.setFormatter(FORMATTERS["json"])  # Use JSON logs for ELK

    # Add Elasticsearch handler to app_logger
    logging.getLogger("app_logger").addHandler(es_handler)
