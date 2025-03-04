"""
Decorators for Logging.

Features:
- `_log_execution`: Logs function execution details, including entry, exit, execution time, and errors.
- Automatically masks sensitive function arguments (e.g., passwords, API keys, tokens).
- Integrates with existing logging system for structured logging.

Environment Variables:
- LOG_LEVEL: Must be explicitly set (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- LOG_FORMAT: `JSON` (default) or `TEXT` for structured vs human-readable logs.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import time
import traceback
from functools import wraps
from typing import Callable, Any
from .custom_logger import get_logger


def _log_execution(func: Callable) -> Callable:
    """
    A decorator that logs when a function starts, finishes, its execution time,
    and captures errors with full traceback if an exception occurs.

    Logs:
    - Function entry with full module path, timestamp, and arguments (excluding sensitive ones).
    - Function exit with execution time (in ms) and return type.
    - Error handling with stack trace logging.

    Args:
        func (Callable): The function whose execution details should be logged.

    Returns:
        Callable: The wrapped function with detailed execution logging.

    Example:
        @_log_execution_time
        def some_function():
            pass
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_logger(func.__module__)
        func_path = f"{func.__module__.split('.')[-1]}.{func.__name__}"

        # Mask sensitive arguments before logging
        SENSITIVE_KEYS = {"password", "token", "apikey", "access_key", "refresh_token"}
        sanitized_args = [str(arg) for arg in args]  # Convert positional args to string
        sanitized_kwargs = {
            k: ("***MASKED***" if k.lower() in SENSITIVE_KEYS else v)
            for k, v in kwargs.items()
        }

        # Capture function start time
        start_time = time.time()
        logger.info(
            f"🚦 START {func_path}() called with args: {sanitized_args}, kwargs: {sanitized_kwargs}"
        )

        try:
            result = func(*args, **kwargs)

            # Capture function end time
            elapsed_time_ms = (time.time() - start_time) * 1000  # Convert to ms
            logger.info(
                f"🏁 FINISH: {func_path}() completed in {elapsed_time_ms:.2f} ms | Return: {type(result).__name__}"
            )
            return result

        except Exception as e:
            logger.error(f"❌ ERROR in {func_path}() ERROR: {e}")
            logger.error(f"🔍 TRACEBACK:\n{traceback.format_exc()}")
            raise  # Re-raise the exception after logging

    return wrapper
