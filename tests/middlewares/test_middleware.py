# tests/middlewares/test_middleware.py

import io
import logging
import pytest
from hestia_logger.middlewares.middleware import LoggingMiddleware


# Dummy request and response objects for testing
class DummyRequest:
    method = "GET"
    url = "http://example.com/test"


class DummyResponse:
    status_code = 200


@pytest.fixture
def capture_middleware_logs():
    """
    Fixture to capture log output from the LoggingMiddleware.
    It attaches a StreamHandler that writes to an in-memory StringIO.
    """
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))

    # Create a LoggingMiddleware instance using a test-specific logger name.
    middleware = LoggingMiddleware(logger_name="test_middleware")
    # Attach our capture handler.
    middleware.logger.addHandler(handler)

    yield stream, handler, middleware

    # Clean up: remove our handler and close the stream.
    middleware.logger.removeHandler(handler)
    stream.close()


def test_log_request(capture_middleware_logs):
    stream, handler, middleware = capture_middleware_logs
    dummy_request = DummyRequest()
    middleware.log_request(dummy_request)
    handler.flush()
    output = stream.getvalue()

    # Verify that the log output contains expected keys and values.
    assert "incoming_request" in output
    assert "GET" in output
    assert "http://example.com/test" in output


def test_log_response(capture_middleware_logs):
    stream, handler, middleware = capture_middleware_logs
    dummy_response = DummyResponse()
    middleware.log_response(dummy_response)
    handler.flush()
    output = stream.getvalue()

    # Verify that the log output contains expected keys and values.
    assert "outgoing_response" in output
    assert "200" in output
