# test_custom_logger.py

import io
import logging
import pytest
from logging import LoggerAdapter
from hestia_logger.core.custom_logger import get_logger, apply_logging_settings

# Ensure logging settings are applied for tests
apply_logging_settings()


@pytest.fixture
def capture_stream():
    """Fixture to capture log output using an in-memory stream."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    yield stream, handler
    stream.close()


def test_get_logger_creates_adapter():
    logger = get_logger("test_service", metadata={"custom_key": "custom_value"})
    # Check that the returned logger is a LoggerAdapter
    assert isinstance(logger, LoggerAdapter)
    # Check that metadata is merged into the adapter extra
    assert "metadata" in logger.extra
    assert logger.extra["metadata"].get("custom_key") == "custom_value"


def test_get_logger_duplicate():
    logger1 = get_logger("dup_service")
    logger2 = get_logger("dup_service")
    # The same instance should be returned for duplicate logger names.
    assert logger1 is logger2


def test_get_logger_app_reserved():
    # Creating a logger with name "app" without internal flag should raise an error.
    with pytest.raises(ValueError):
        get_logger("app")


def test_logger_output(capture_stream):
    stream, handler = capture_stream
    # Get a logger and attach our capture handler to its underlying logger.
    logger = get_logger("output_test")
    logger.logger.addHandler(handler)

    test_message = "Hello, logging test"
    logger.info(test_message)
    handler.flush()
    output = stream.getvalue()
    # Check that the test message is in the captured output.
    assert test_message in output
    # Clean up the handler.
    logger.logger.removeHandler(handler)
