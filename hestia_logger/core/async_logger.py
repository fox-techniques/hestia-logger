"""
Hestia Logger - Async Logger.

This module provides optional async logging for specific use cases where
thread-based logging might not be suitable.

Currently, Hestia Logger defaults to thread-based logging. If async logging
is required, this module can be extended.

"""

import logging
import asyncio
import aiofiles
from ..internal_logger import hestia_internal_logger

__all__ = ["AsyncFileLogger"]


class AsyncFileLogger(logging.Handler):
    """
    Asynchronous file logger for specialized use cases.

    This class is not used by default in Hestia Logger. Instead, it serves
    as an experimental implementation if async file logging is required.

    Example Use:
        logger = AsyncFileLogger("async_app.log")
        logging.getLogger("async_test").addHandler(logger)

    """

    def __init__(self, log_file: str):
        super().__init__()
        self.log_file = log_file
        self.loop = asyncio.get_event_loop()

    async def _write_log(self, message):
        """
        Writes log messages asynchronously to the file.
        """
        try:
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
        """
        Formats log records and ensures `_write_log()` runs asynchronously.
        """
        log_entry = self.format(record)
        hestia_internal_logger.debug(f"🔄 Handling log record in emit(): {log_entry}")

        try:
            if self.loop.is_running():
                self.loop.create_task(self._write_log(log_entry))
            else:
                asyncio.run(self._write_log(log_entry))
        except Exception as e:
            hestia_internal_logger.error(f"❌ ERROR IN `emit()`: {e}")
