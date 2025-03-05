"""
Utils Module Initialization.

This module initializes async request logging and exposes utilities.

Features:
- Provides async HTTP request logging.
- Ensures `httpx` integration for non-blocking network logging.
- Enables automatic request logging when imported.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import threading
import asyncio
from .requests_logger import enable_request_logging, async_http_request


def _run_background_tasks():
    """
    Runs async setup tasks in a background thread.

    This ensures that async functions can run properly
    even when no event loop is running at import time.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(enable_request_logging())


# Start the background thread for async setup
threading.Thread(target=_run_background_tasks, daemon=True).start()


__all__ = [
    "async_http_request",
    "enable_request_logging",
]
