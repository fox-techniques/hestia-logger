import functools
import time
import asyncio
import json
from hestia_logger.core.custom_logger import get_logger

SENSITIVE_KEYS = {"password", "token", "secret", "apikey", "api_key"}


def mask_sensitive_data(kwargs):
    """Masks sensitive data in function arguments."""
    return {
        key: "***" if key.lower() in SENSITIVE_KEYS else value
        for key, value in kwargs.items()
    }


def log_execution(name="hestia_decorator", log_level="INFO"):
    """
    Decorator for logging function execution details with async support.

    :param name: Logger name (defaults to 'hestia_decorator').
    :param log_level: Logging level (defaults to 'INFO').
    """

    def decorator(func):
        logger = get_logger(name)
        app_logger = get_logger("app")  # Ensure logs are forwarded to app.log

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            sanitized_kwargs = mask_sensitive_data(kwargs)

            log_entry = {
                "event": "Async Execution",
                "function": func.__name__,
                "args": args,
                "kwargs": sanitized_kwargs,
                "status": "started",
            }
            logger.info(
                f"🔍 {func.__name__} execution started.", extra={"json": log_entry}
            )
            app_logger.info(json.dumps(log_entry))  # Send JSON log to app.log

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                log_entry.update(
                    {
                        "status": "completed",
                        "duration": f"{duration:.4f} sec",
                        "result": result,
                    }
                )
                logger.info(
                    f"✅ {func.__name__} completed in {duration:.4f} sec.",
                    extra={"json": log_entry},
                )
                app_logger.info(json.dumps(log_entry))  # Send JSON log to app.log

                return result
            except Exception as e:
                log_entry.update({"status": "error", "error": str(e)})
                logger.error(
                    f"❌ Exception in {func.__name__}: {e}",
                    exc_info=True,
                    extra={"json": log_entry},
                )
                app_logger.error(json.dumps(log_entry))  # Send JSON log to app.log

                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            sanitized_kwargs = mask_sensitive_data(kwargs)

            log_entry = {
                "event": "Sync Execution",
                "function": func.__name__,
                "args": args,
                "kwargs": sanitized_kwargs,
                "status": "started",
            }
            logger.info(
                f"🔍 {func.__name__} execution started.", extra={"json": log_entry}
            )
            app_logger.info(json.dumps(log_entry))  # Send JSON log to app.log

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                log_entry.update(
                    {
                        "status": "completed",
                        "duration": f"{duration:.4f} sec",
                        "result": result,
                    }
                )
                logger.info(
                    f"✅ {func.__name__} completed in {duration:.4f} sec.",
                    extra={"json": log_entry},
                )
                app_logger.info(json.dumps(log_entry))  # Send JSON log to app.log

                return result
            except Exception as e:
                log_entry.update({"status": "error", "error": str(e)})
                logger.error(
                    f"❌ Exception in {func.__name__}: {e}",
                    exc_info=True,
                    extra={"json": log_entry},
                )
                app_logger.error(json.dumps(log_entry))  # Send JSON log to app.log

                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
