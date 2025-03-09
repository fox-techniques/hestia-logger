import functools
import time
import asyncio
import json
import logging
import inspect
from hestia_logger.core.custom_logger import get_logger

SENSITIVE_KEYS = {"password", "token", "secret", "apikey", "api_key"}


def mask_sensitive_data(kwargs):
    """Masks sensitive data in function arguments."""
    return {
        key: "***" if key.lower() in SENSITIVE_KEYS else value
        for key, value in kwargs.items()
    }


def log_execution(func):
    """
    Logs function execution start, end, and duration.
    - Ensures structured JSON logs are written correctly.
    """

    frame = inspect.currentframe().f_back
    service_logger = frame.f_globals.get("my_service_logger") or get_logger(
        func.__module__
    )
    app_logger = get_logger("app", internal=True)

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        sanitized_kwargs = mask_sensitive_data(kwargs)

        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
            "service": service_logger.name,
            "function": func.__name__,
            "status": "started",
            "args": args,
            "kwargs": sanitized_kwargs,
        }

        app_logger.info(log_entry)  # No json.dumps()
        service_logger.info(f"📌 Started: {func.__name__}()")

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time

            log_entry.update(
                {
                    "status": "completed",
                    "duration": f"{duration:.4f} sec",
                    "result": str(result),
                }
            )

            app_logger.info(log_entry)  # No json.dumps()
            service_logger.info(f"✅ Finished: {func.__name__}() in {duration:.4f} sec")

            return result
        except Exception as e:
            log_entry.update({"status": "error", "error": str(e)})

            app_logger.error(log_entry)  # No json.dumps()
            service_logger.error(f"❌ Error in {func.__name__}: {e}")

            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        sanitized_kwargs = mask_sensitive_data(kwargs)

        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
            "service": service_logger.name,
            "function": func.__name__,
            "status": "started",
            "args": args,
            "kwargs": sanitized_kwargs,
        }

        # Correct JSON logging
        app_logger.info(log_entry)  # No json.dumps()
        service_logger.info(f"📌 Started: {func.__name__}()")

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            log_entry.update(
                {
                    "status": "completed",
                    "duration": f"{duration:.4f} sec",
                    "result": str(result),
                }
            )

            app_logger.info(log_entry)  # No json.dumps()
            service_logger.info(f"✅ Finished: {func.__name__}() in {duration:.4f} sec")

            return result
        except Exception as e:
            log_entry.update({"status": "error", "error": str(e)})

            app_logger.error(log_entry)  # No json.dumps()
            service_logger.error(f"❌ Error in {func.__name__}: {e}")

            raise

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
