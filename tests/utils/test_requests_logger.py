# test_requests_logger.py

import io
import json
import logging
import pytest
from hestia_logger.utils.requests_logger import requests_logger


@pytest.fixture
def capture_requests_logger(monkeypatch):
    """
    Fixture that replaces the requests_logger handlers with a StreamHandler
    that writes to an in-memory StringIO, so we can capture and inspect the output.
    """
    stream = io.StringIO()
    # Create a new handler with JSON formatting from our formatter.
    from hestia_logger.core.formatters import JSONFormatter

    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())

    # Replace existing handlers with our test handler.
    original_handlers = requests_logger.handlers
    requests_logger.handlers = [handler]

    yield stream, handler

    # Restore original handlers after the test.
    requests_logger.handlers = original_handlers
    stream.close()


def test_requests_logger_output(capture_requests_logger):
    stream, handler = capture_requests_logger
    test_message = "Test requests logger message"

    # Log a simple JSON string message. The logger is set up to use JSONFormatter.
    requests_logger.info(test_message)

    handler.flush()
    output = stream.getvalue().strip()

    # The output may consist of multiple lines if multiple handlers log;
    # for our test we expect one log line.
    lines = output.splitlines()
    assert len(lines) >= 1, "No log output captured."

    # Parse the first log entry
    log_entry = json.loads(lines[0])

    # Verify that standardized keys are present.
    assert "timestamp" in log_entry, "Missing 'timestamp' key."
    assert (
        "level" in log_entry and log_entry["level"] == "INFO"
    ), "Incorrect or missing 'level' key."
    assert "service" in log_entry, "Missing 'service' key."

    # Verify that the message content is captured.
    # Depending on your formatter logic, the message may be nested or directly included.
    if "message" in log_entry:
        assert (
            test_message in log_entry["message"]
        ), "Test message not found in 'message' field."
    else:
        # If your formatter merges the message into the log_entry directly.
        found = any(test_message in str(value) for value in log_entry.values())
        assert found, "Test message not found in log entry."
