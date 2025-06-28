# tests/decorators/test_decorators.py

import sys
import logging
import logging.handlers
import asyncio
import pytest
import importlib

# 1) Monkey-patch file handlers to avoid permission issues
logging.handlers.RotatingFileHandler = lambda *args, **kwargs: logging.StreamHandler(
    sys.stdout
)
logging.handlers.TimedRotatingFileHandler = (
    lambda *args, **kwargs: logging.StreamHandler(sys.stdout)
)

# 2) Import the actual decorator and helpers
dec = importlib.import_module("hestia_logger.decorators.decorators")
log_execution = dec.log_execution
mask_sensitive_data = dec.mask_sensitive_data
sanitize_module_name = dec.sanitize_module_name
redact_large = dec.redact_large
safe_serialize = dec.safe_serialize


# 3) ListHandler to capture "app" logs in memory
class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


@pytest.fixture(autouse=True)
def capture_app_logs():
    logger = logging.getLogger("app")
    logger.handlers.clear()
    handler = ListHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    yield handler
    logger.handlers.clear()


# 4) Helper-function tests
def test_mask_sensitive_data_deep():
    data = {
        "a": {"password": "secret", "nested": [{"token": "tok", "keep": "val"}]},
        "normal": "yes",
    }
    out = mask_sensitive_data(data)
    assert out["a"]["password"] == "***"
    assert out["a"]["nested"][0]["token"] == "***"
    assert out["a"]["nested"][0]["keep"] == "val"
    assert out["normal"] == "yes"


def test_sanitize_module_name():
    assert sanitize_module_name("__mod__") == "mod"
    assert sanitize_module_name("regular") == "regular"


def test_redact_large():
    assert redact_large("hi", max_length=5) == "hi"
    long = "x" * 10
    r = redact_large(long, max_length=4)
    assert r.endswith("... [TRUNCATED]")


def test_log_execution_error(capture_app_logs):
    @log_execution(logger_name="unit", max_length=50)
    def bad():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        bad()

    msgs = [r.getMessage() for r in capture_app_logs.records]
    assert any("'status': 'error'" in m for m in msgs)
    assert any("boom" in m for m in msgs)
    assert any("traceback" in m for m in msgs)


@pytest.mark.asyncio
async def test_log_execution_async(capture_app_logs):
    @log_execution(logger_name="unit", max_length=50)
    async def mul(a, b):
        await asyncio.sleep(0.001)
        return a * b

    assert await mul(4, 5) == 20

    msgs = [r.getMessage() for r in capture_app_logs.records]
    # Only assert the 'completed' entry (start may race)
    assert any("'status': 'completed'" in m for m in msgs)
