"""
Async File Log Handlers.

This module provides asynchronous file-based logging using `aiofiles`.
It ensures non-blocking log writing and proper error handling in async environments.

Features:
- Supports structured JSON logs (`app.log`).
- Writes plain-text logs for easier debugging (`all.log`).
- Non-blocking execution via `asyncio.create_task()`.
- Safe fallback to synchronous execution if no event loop is running.
- Error handling with detailed internal logging.

Log Files:
- `app.log` → Stores structured JSON logs.
- `all.log` → Stores all logs in a human-readable format.

Usage:
This module is used internally by Hestia Logger and should not be imported directly.
Handlers (`file_handler_app` and `file_handler_all`) are automatically registered.


Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
import aiofiles
import asyncio
import os
from ..core.config import LOG_FILE_PATH_APP, LOG_FILE_PATH_ALL, LOG_LEVEL
from ..internal_logger import hestia_internal_logger

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH_APP), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE_PATH_ALL), exist_ok=True)


class DebugAsyncFileHandler(logging.Handler):
    """
    Async file handler that ensures logs are written properly.
    """

    def __init__(self, log_file):
        super().__init__()
        self.log_file = log_file
        self.loop = asyncio.get_event_loop()

    async def _write_log(self, message):
        """Writes log messages asynchronously and ensures flush."""
        try:
            hestia_internal_logger.debug(
                f"📝 Attempting to write log to {self.log_file}..."
            )
            async with aiofiles.open(self.log_file, mode="a") as f:
                await f.write(message + "\n")
                await f.flush()
            hestia_internal_logger.debug(
                f"✅ Successfully wrote log to {self.log_file}."
            )
        except Exception as e:
            hestia_internal_logger.error(
                f"❌ ERROR WRITING TO FILE {self.log_file}: {e}"
            )

    def emit(self, record):
        """Formats log records and ensures `_write_log()` runs asynchronously."""
        log_entry = self.format(record)
        hestia_internal_logger.debug(f"🔄 Handling log record in emit(): {log_entry}")

        try:
            if self.loop.is_running():
                self.loop.create_task(self._write_log(log_entry))
            else:
                asyncio.run(self._write_log(log_entry))  # Force execution in sync mode
        except Exception as e:
            hestia_internal_logger.error(f"❌ ERROR IN `emit()`: {e}")


# JSON and plain text formatters
FORMATTERS = {
    "json": logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    ),
    "plain": logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
}

# Async file handlers
file_handler_app = DebugAsyncFileHandler(LOG_FILE_PATH_APP)  # Structured JSON logs
file_handler_all = DebugAsyncFileHandler(LOG_FILE_PATH_ALL)  # Human-readable logs
file_handler_app.setLevel(LOG_LEVEL)
file_handler_all.setLevel(LOG_LEVEL)
file_handler_app.setFormatter(FORMATTERS["json"])
file_handler_all.setFormatter(FORMATTERS["plain"])
