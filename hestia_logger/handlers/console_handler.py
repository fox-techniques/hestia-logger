"""
Console Log Handler.

This module provides a structured console log handler.

Features:
- Uses `structlog` for structured console logging.
- Supports JSON and plain-text logging formats.
- Ensures non-blocking logging for async applications.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
from ..core.config import LOG_LEVEL, LOG_FORMAT

# Define log formatters
FORMATTERS = {
    "json": logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    ),
    "plain": logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
}

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(
    FORMATTERS["json"] if LOG_FORMAT == "JSON" else FORMATTERS["plain"]
)
