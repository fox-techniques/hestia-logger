"""
Async-Compatible Logging Decorators.

This module provides logging decorators that:
- Log function entry, exit, and execution time.
- Support both synchronous and asynchronous functions.
- Use `structlog` for structured JSON logging.
- Mask sensitive parameters like passwords and API keys.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import time
import traceback
import asyncio
from functools import wraps
from typing import Callable, Any
from structlog import get_logger

logger = get_logger("decorators")


def _log_execution(func: Callable) -> Callable:
    """
    A decorator that logs function entry, exit, and execution time.

    - Automatically detects if the function is async or sync.
    - Logs function name, execution time, and return type.
    - Masks sensitive arguments like passwords and API keys.
    - Captures and logs full error stack traces.

    Args:
        func (Callable): The function to log.

    Returns:
        Callable: Wrapped function with async-compatible logging.
    """

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        return await _execute_and_log(func, args, kwargs, is_async=True)

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        return _execute_and_log(func, args, kwargs, is_async=False)

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


async def _execute_and_log(func: Callable, args: Any, kwargs: Any, is_async: bool):
    """
    Executes the function and logs its execution details.

    Args:
        func (Callable): The function being executed.
        args (Any): Positional arguments.
        kwargs (Any): Keyword arguments.
        is_async (bool): Whether the function is async.

    Returns:
        Any: The result of the function execution.
    """

    func_path = f"{func.__module__.split('.')[-1]}.{func.__name__}"

    # Mask sensitive arguments
    SENSITIVE_KEYS = {"password", "token", "apikey", "access_key", "refresh_token"}
    sanitized_args = [str(arg) for arg in args]  # Convert args to strings
    sanitized_kwargs = {
        k: ("***MASKED***" if k.lower() in SENSITIVE_KEYS else v)
        for k, v in kwargs.items()
    }

    # Log function start
    start_time = time.time()
    await logger.info(
        "🚦 START Function Execution",
        function=func_path,
        args=sanitized_args,
        kwargs=sanitized_kwargs,
    )

    try:
        if is_async:
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)

        # Log function completion
        elapsed_time_ms = (time.time() - start_time) * 1000  # Convert to ms
        await logger.info(
            "🏁 FINISH Function Execution",
            function=func_path,
            execution_time=f"{elapsed_time_ms:.2f}ms",
            return_type=type(result).__name__,
        )

        return result

    except Exception as e:
        # Log errors
        await logger.error(
            "❌ ERROR in Function Execution",
            function=func_path,
            error=str(e),
            traceback=traceback.format_exc(),
        )
        raise  # Re-raise exception
