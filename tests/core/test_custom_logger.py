import io
import logging
import pytest
from logging import LoggerAdapter
from hestia_logger.core.custom_logger import get_logger, apply_logging_settings

# Apply global logger config
apply_logging_settings()


@pytest.fixture
def capture_stream():
    """Fixture to capture log output using an in-memory stream."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)  # Required for visible output
    yield stream, handler
    stream.close()


import os
import tempfile


import os
import tempfile
import importlib
import pytest
from logging import LoggerAdapter


def test_get_logger_creates_adapter(monkeypatch):
    # Set LOGS_DIR to a temporary writable location
    tmp_log_dir = tempfile.mkdtemp()
    monkeypatch.setenv("LOGS_DIR", tmp_log_dir)

    # Reload config first to pick up new LOGS_DIR
    from hestia_logger.core import config

    importlib.reload(config)

    # Now reload the logger module that depends on config
    from hestia_logger.core import custom_logger

    importlib.reload(custom_logger)

    logger = custom_logger.get_logger(
        "test_service", metadata={"custom_key": "custom_value"}
    )

    assert isinstance(logger, LoggerAdapter)
    assert "metadata" in logger.extra
    assert logger.extra["metadata"].get("custom_key") == "custom_value"


def test_get_logger_duplicate():
    logger1 = get_logger("dup_service")
    logger2 = get_logger("dup_service")
    assert logger1 is logger2


def test_get_logger_app_reserved():
    with pytest.raises(ValueError):
        get_logger("app")


def test_logger_output(capture_stream):
    stream, handler = capture_stream
    logger = get_logger("output_test")
    logger.logger.setLevel(logging.DEBUG)
    logger.logger.addHandler(handler)

    test_message = "Hello, logging test"
    logger.info(test_message)
    handler.flush()

    output = stream.getvalue()
    assert test_message in output

    logger.logger.removeHandler(handler)
