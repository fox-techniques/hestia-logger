import sys
import os
from io import StringIO
import pytest
import asyncio
import logging
from unittest.mock import patch

# --- Early patch to avoid writing to /var/logs ---
with patch.dict(
    os.environ,
    {
        "LOG_FILE_PATH": "./logs/test_app.log",
        "LOG_FILE_PATH_INTERNAL": "./logs/test_internal.log",
    },
):
    from hestia_logger.decorators import log_execution


def get_test_log_stream():
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))

    logger = logging.getLogger("app")
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger, stream


@log_execution(logger_name="test_logger", max_length=50)
def sync_func(password, notes):
    return {"status": "ok", "notes": notes}


@log_execution(logger_name="test_logger", max_length=50)
async def async_func(token, data):
    await asyncio.sleep(0.01)
    return {"token": token, "summary": data}


@log_execution(logger_name="test_logger")
def error_func():
    raise RuntimeError("Simulated error")


def test_sync_logging_behavior():
    _, stream = get_test_log_stream()
    result = sync_func(password="supersecret", notes="hi")

    logs = stream.getvalue()
    assert result["status"] == "ok"
    assert '"password": "***"' in logs
    assert "sync_func" in logs
    assert "started" in logs
    assert "completed" in logs


def test_redaction_and_truncation():
    _, stream = get_test_log_stream()
    sync_func(password="123", notes="X" * 200)

    logs = stream.getvalue()
    assert "... [TRUNCATED]" in logs
    assert '"password": "***"' in logs


@pytest.mark.asyncio
async def test_async_logging_behavior():
    _, stream = get_test_log_stream()
    await async_func(token="abc123", data="Y" * 150)

    logs = stream.getvalue()
    assert '"token": "***"' in logs
    assert "... [TRUNCATED]" in logs


def test_error_logging():
    _, stream = get_test_log_stream()
    with pytest.raises(RuntimeError):
        error_func()

    logs = stream.getvalue()
    assert '"status": "error"' in logs
    assert "Simulated error" in logs
    assert "traceback" in logs
