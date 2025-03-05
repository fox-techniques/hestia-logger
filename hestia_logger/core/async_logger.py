"""
Async Logger Module.

This module provides an asynchronous logging system using `asyncio.Queue` to 
ensure non-blocking logging. Logs are processed in the background without affecting 
application performance.

Features:
- Uses `structlog` for structured JSON logging.
- Supports async log processing with `asyncio.Queue`.
- Handles logs for FastAPI applications efficiently.
- Ensures compatibility with Elasticsearch, file, and console logging.
- Provides a global async log worker that runs in the background.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import asyncio
import structlog
from threading import Thread

from ..internal_logger import hestia_internal_logger

# Async log queue for non-blocking logging
log_queue = asyncio.Queue()


class AsyncLogWorker:
    """
    Background async worker that continuously processes log messages.

    This worker runs in a separate thread to ensure logs are processed
    asynchronously without blocking the main event loop.
    """

    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self._start_worker, daemon=True)
        self.thread.start()

    def _start_worker(self):
        """Starts the async log processing worker in a dedicated thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._worker())

    async def _worker(self):
        """Continuously processes log messages from the queue."""
        while True:
            log_entry = await self.queue.get()
            if log_entry is None:
                break  # Stop worker gracefully

            hestia_internal_logger.info(f"Log entry: {log_entry}")

    def stop(self):
        """Stops the log worker by sending a termination signal."""
        self.queue.put_nowait(None)


# Start the global async log worker
log_worker = AsyncLogWorker(log_queue)


async def log_async(message: str, level: str = "info", **kwargs):
    """
    Queues log messages asynchronously to avoid blocking the event loop.

    Args:
        message (str): The log message.
        level (str): The log level (`debug`, `info`, `warning`, `error`).
        **kwargs: Additional metadata to include in the log entry.
    """
    await log_queue.put({"level": level, "message": message, **kwargs})


# Configure structlog for async logging
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(),  # JSON output for structured logs
    ],
    context_class=dict,
    wrapper_class=structlog.make_filtering_bound_logger(),
    logger_factory=structlog.PrintLoggerFactory(),
)
