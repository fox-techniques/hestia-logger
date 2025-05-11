# tests/middlewares/test_middleware.py

import io
import logging
import pytest
from hestia_logger.middlewares.middleware import LoggingMiddleware


# --- Dummy request/response classes --- #


class DummyState:
    request_id = "test-request-id"


class DummyURL:
    def __init__(self, path="/test", query=""):
        self.path = path
        self.query = query

    def __str__(self):
        if self.query:
            return f"http://localhost{self.path}?{self.query}"
        return f"http://localhost{self.path}"


class DummyRequest:
    method = "GET"
    url = DummyURL()
    client = type("Client", (), {"host": "127.0.0.1"})()
    headers = {"user-agent": "pytest", "host": "localhost"}
    state = DummyState()


class DummyResponse:
    status_code = 200


# --- Middleware capture fixture --- #


@pytest.fixture
def capture_middleware_logs():
    """
    Fixture to capture log output from the LoggingMiddleware.
    It attaches a StreamHandler that writes to an in-memory StringIO.
    """
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))

    middleware = LoggingMiddleware(logger_name="test_middleware")
    middleware.logger.addHandler(handler)

    yield stream, handler, middleware

    middleware.logger.removeHandler(handler)
    stream.close()


# --- Tests --- #


def test_log_request(capture_middleware_logs):
    stream, handler, middleware = capture_middleware_logs
    dummy_request = DummyRequest()
    middleware.log_request(dummy_request)
    handler.flush()
    output = stream.getvalue()

    assert "incoming_request" in output
    assert "GET" in output
    assert "/test" in output


def test_log_response(capture_middleware_logs):
    stream, handler, middleware = capture_middleware_logs
    dummy_request = DummyRequest()
    dummy_response = DummyResponse()

    middleware.log_response(dummy_request, dummy_response)
    handler.flush()
    output = stream.getvalue()

    assert "outgoing_response" in output
    assert "200" in output
