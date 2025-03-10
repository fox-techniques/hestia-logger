# test_decorators.py

import asyncio
import io
import json
import logging
import pytest
import time

from hestia_logger.decorators.decorators import (
    mask_sensitive_data,
    sanitize_module_name,
    safe_serialize,
    log_execution,
)
from hestia_logger.core.custom_logger import get_logger

# --- Tests for helper functions ---


def test_mask_sensitive_data():
    input_kwargs = {
        "username": "user1",
        "password": "secret123",
        "apikey": "abc123",
        "email": "user@example.com",
    }
    masked = mask_sensitive_data(input_kwargs)
    assert masked["username"] == "user1"
    assert masked["password"] == "***"
    assert masked["apikey"] == "***"
    assert masked["email"] == "user@example.com"


def test_sanitize_module_name():
    assert sanitize_module_name("__main__") == "main"
    assert sanitize_module_name("my_module") == "my_module"
    assert sanitize_module_name("__config__") == "config"


def test_safe_serialize_serializable():
    data = {"key": "value", "number": 42}
    serialized = safe_serialize(data)
    parsed = json.loads(serialized)
    assert parsed == data


def test_safe_serialize_nonserializable():
    non_serializable = lambda x: x
    result = safe_serialize(non_serializable)
    assert isinstance(result, str)
    assert "function" in result or "lambda" in result


# --- Fixtures to capture logs ---


@pytest.fixture
def capture_service_logger():
    """
    Attaches a temporary StreamHandler to the service logger (for the decorated function)
    and returns the stream, handler, and the service logger.
    """
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))

    service_logger = get_logger("decorator_test")
    # For LoggerAdapter, attach to its underlying logger; otherwise attach directly.
    if hasattr(service_logger, "logger"):
        service_logger.logger.addHandler(handler)
    else:
        service_logger.addHandler(handler)

    yield stream, handler, service_logger

    if hasattr(service_logger, "logger"):
        service_logger.logger.removeHandler(handler)
    else:
        service_logger.removeHandler(handler)
    stream.close()


@pytest.fixture
def capture_app_logger():
    """
    Attaches a temporary StreamHandler to the app logger (internal logger) and returns
    the stream, handler, and the app logger.
    """
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))

    app_logger = get_logger("app", internal=True)
    if hasattr(app_logger, "logger"):
        app_logger.logger.addHandler(handler)
    else:
        app_logger.addHandler(handler)

    yield stream, handler, app_logger

    if hasattr(app_logger, "logger"):
        app_logger.logger.removeHandler(handler)
    else:
        app_logger.removeHandler(handler)
    stream.close()


# --- Tests for the log_execution decorator ---


def test_log_execution_sync(capture_service_logger, capture_app_logger):
    service_stream, service_handler, _ = capture_service_logger
    app_stream, app_handler, _ = capture_app_logger

    @log_execution(logger_name="decorator_test")
    def add(a, b, password="default"):
        return a + b

    result = add(3, 4, password="should_be_masked")
    assert result == 7

    service_handler.flush()
    app_handler.flush()
    combined_output = service_stream.getvalue() + app_stream.getvalue()

    # Check for start/finish markers
    assert "Started" in combined_output, "Expected 'Started' marker in log output"
    assert "Finished" in combined_output, "Expected 'Finished' marker in log output"
    # Check that the sensitive data in kwargs is masked in at least one of the outputs.
    assert "***" in combined_output, "Expected masked sensitive data in log output"


@pytest.mark.asyncio
async def test_log_execution_async(capture_service_logger, capture_app_logger):
    service_stream, service_handler, _ = capture_service_logger
    app_stream, app_handler, _ = capture_app_logger

    @log_execution(logger_name="decorator_test")
    async def multiply(a, b, token="default"):
        await asyncio.sleep(0.1)
        return a * b

    result = await multiply(3, 5, token="should_be_masked")
    assert result == 15

    service_handler.flush()
    app_handler.flush()
    combined_output = service_stream.getvalue() + app_stream.getvalue()

    assert "Started" in combined_output, "Expected 'Started' marker in log output"
    assert "Finished" in combined_output, "Expected 'Finished' marker in log output"
    assert "***" in combined_output, "Expected masked sensitive data in log output"
