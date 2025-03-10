import functools
import time
import asyncio
import json
import inspect
import traceback
from hestia_logger.core.custom_logger import get_logger

SENSITIVE_KEYS = {"password", "token", "secret", "apikey", "api_key"}


def mask_sensitive_data(kwargs):
    """Masks sensitive data in function arguments."""
    return {
        key: "***" if key.lower() in SENSITIVE_KEYS else value
        for key, value in kwargs.items()
    }


def sanitize_module_name(module_name):
    """Converts "__module__" format to "module_module" for cleaner log file names."""
    if module_name.startswith("__") and module_name.endswith("__"):
        return f"{module_name.strip('_')}"
    return module_name


def safe_serialize(obj):
    """Safely serialize objects to JSON, handling non-serializable cases."""
    try:
        return json.dumps(obj, ensure_ascii=False)
    except TypeError:
        return str(obj)  # Fallback for non-serializable objects


def log_execution(func=None, *, logger_name=None):
    if func is None:
        return lambda f: log_execution(f, logger_name=logger_name)

    module_name = func.__module__
    sanitized_name = sanitize_module_name(module_name)
    service_logger = get_logger(logger_name or sanitized_name)
    app_logger = get_logger("app", internal=True)

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            # Include positional arguments in kwargs for masking
            args_names = inspect.signature(func).parameters.keys()
            all_kwargs = {**dict(zip(args_names, args)), **kwargs}
            sanitized_kwargs = mask_sensitive_data(all_kwargs)
            log_entry = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
                "service": service_logger.name,
                "function": func.__name__,
                "status": "started",
                "args": safe_serialize(args),
                "kwargs": safe_serialize(sanitized_kwargs),
            }
            app_logger.info(json.dumps(log_entry, ensure_ascii=False))
            service_logger.info(f"📌 Started: {func.__name__}()")
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                log_entry.update(
                    {
                        "status": "completed",
                        "duration": f"{duration:.4f} sec",
                        "result": safe_serialize(result),
                    }
                )
                app_logger.info(json.dumps(log_entry, ensure_ascii=False))
                service_logger.info(
                    f"✅ Finished: {func.__name__}() in {duration:.4f} sec"
                )
                return result
            except Exception as e:
                log_entry.update(
                    {
                        "status": "error",
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )
                app_logger.error(json.dumps(log_entry, ensure_ascii=False))
                service_logger.error(f"❌ Error in {func.__name__}: {e}")
                raise

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            sanitized_kwargs = mask_sensitive_data(kwargs)
            log_entry = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
                "service": service_logger.name,
                "function": func.__name__,
                "status": "started",
                "args": safe_serialize(args),
                "kwargs": safe_serialize(sanitized_kwargs),
            }
            app_logger.info(json.dumps(log_entry, ensure_ascii=False))
            service_logger.info(f"📌 Started: {func.__name__}()")
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_entry.update(
                    {
                        "status": "completed",
                        "duration": f"{duration:.4f} sec",
                        "result": safe_serialize(result),
                    }
                )
                app_logger.info(json.dumps(log_entry, ensure_ascii=False))
                service_logger.info(
                    f"✅ Finished: {func.__name__}() in {duration:.4f} sec"
                )
                return result
            except Exception as e:
                log_entry.update(
                    {
                        "status": "error",
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )
                app_logger.error(json.dumps(log_entry, ensure_ascii=False))
                service_logger.error(f"❌ Error in {func.__name__}: {e}")
                raise

        return sync_wrapper
