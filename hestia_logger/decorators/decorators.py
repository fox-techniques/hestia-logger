import functools
import time
import asyncio
import logging
import json
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
    Ensures only structured JSON logs go to `app.log`.
    """

    module = inspect.getmodule(func)
    module_logger = None

    if module:
        for attr_name in dir(module):
            attr_value = getattr(module, attr_name)
            if isinstance(attr_value, logging.Logger):
                module_logger = attr_value
                print(f"✅ Using existing logger: {module_logger.name}")
                break

    if not module_logger:
        module_logger = get_logger(func.__module__)

    app_logger = get_logger("app", internal=True)

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
            "service": module_logger.name,
            "event": "Async Execution",
            "function": func.__name__,
            "status": "started",
        }

        # ✅ Log only JSON to `app.log`
        app_logger.info(json.dumps(log_entry))

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

            app_logger.info(json.dumps(log_entry))
            return result
        except Exception as e:
            log_entry.update({"status": "error", "error": str(e)})
            app_logger.error(json.dumps(log_entry))
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
            "service": module_logger.name,
            "event": "Sync Execution",
            "function": func.__name__,
            "status": "started",
        }

        # ✅ Log only JSON to `app.log`
        app_logger.info(json.dumps(log_entry))

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

            app_logger.info(json.dumps(log_entry))
            return result
        except Exception as e:
            log_entry.update({"status": "error", "error": str(e)})
            app_logger.error(json.dumps(log_entry))
            raise

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
