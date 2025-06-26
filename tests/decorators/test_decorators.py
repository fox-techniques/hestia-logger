import asyncio
import inspect
import json
import pytest

import hestia_logger.decorators.decorators as decorators
from hestia_logger.decorators.decorators import (
    mask_string,
    deep_mask,
    safe_serialize,
    get_caller_script_name,
    log_execution,
)


class DummyLogger:
    def __init__(self, name):
        self.name = name
        self.infos = []
        self.errors = []

    def info(self, msg):
        self.infos.append(msg)

    def error(self, msg):
        self.errors.append(msg)


def test_mask_string_query_and_url():
    # query-param style
    s = "user=foo&password=sekrit&token=abcd1234&x=1"
    out = mask_string(s)
    assert "password=***" in out
    assert "token=***" in out
    assert "sekrit" not in out and "abcd1234" not in out

    # URL-auth style
    u = "postgresql://joe:hunter2@db.local/mydb"
    out2 = mask_string(u)
    assert "://joe:***@db.local" in out2
    assert "hunter2" not in out2


def test_deep_mask_various_structures():
    data = {
        "password": "p",
        "nested": {"token": "t", "keep": 42},
        "lst": ["normal", {"apikey": "123"}],
        "tuple": ("foo", "secret=bad"),
        "num": 7,
    }
    masked = deep_mask(data)
    assert masked["password"] == "***"
    assert masked["nested"]["token"] == "***"
    assert masked["nested"]["keep"] == 42
    assert masked["lst"][0] == "normal"
    assert masked["lst"][1]["apikey"] == "***"
    assert isinstance(masked["tuple"], tuple)
    assert masked["tuple"][1] == "secret=***"
    assert masked["num"] == 7


def test_safe_serialize_json_and_fallback():
    # JSON-serializable object
    data = {"password": "x", "a": 1}
    dumped = safe_serialize(data)
    obj = json.loads(dumped)
    assert obj["password"] == "***"
    assert obj["a"] == 1

    # non-serializable object → fallback to masked string
    class Foo:
        pass

    data2 = {"token": "tok", "obj": Foo()}
    out = safe_serialize(data2)
    assert isinstance(out, str)
    assert "***" in out
    # ensure the original value wasn't left unmasked
    # check that ': 'tok'' doesn't appear (value masked)
    assert ": 'tok'" not in out


def test_get_caller_script_name_ignores_pytest(monkeypatch):
    FakeFrame = lambda fn: type("F", (), {"filename": fn})
    fake = [
        FakeFrame("/usr/lib/python3.10/site-packages/pytest/x.py"),
        FakeFrame("/home/me/projects/myscript.py"),
    ]
    monkeypatch.setattr(inspect, "stack", lambda: fake)
    name = get_caller_script_name()
    assert name == "myscript"


def test_log_execution_sync_success(monkeypatch):
    created = []

    def fake_get_logger(name, internal=False):
        lg = DummyLogger(name)
        created.append(lg)
        return lg

    monkeypatch.setattr(decorators, "get_logger", fake_get_logger)

    @log_execution
    def add(a, b, password="nope"):
        return a + b

    assert add(2, 3, password="hunter2") == 5
    service_logger, app_logger = created
    assert len(app_logger.infos) == 2
    start = json.loads(app_logger.infos[0])
    assert start["status"] == "started"
    assert "hunter2" not in start["kwargs"]
    assert "***" in start["kwargs"]
    done = json.loads(app_logger.infos[1])
    assert done["status"] == "completed"
    assert done["result"] == "5"


def test_log_execution_sync_error(monkeypatch):
    created = []

    def fake_get_logger(name, internal=False):
        logger = DummyLogger(name)
        created.append(logger)
        return logger

    monkeypatch.setattr(decorators, "get_logger", fake_get_logger)

    @log_execution
    def boom(x):
        raise RuntimeError("kaboom")

    with pytest.raises(RuntimeError):
        boom(1)

    # Find the app logger (internal=True) and check the error log
    app_logger = next(lg for lg in created if lg.name == "app" and lg.errors)
    assert len(app_logger.errors) == 1

    err = json.loads(app_logger.errors[0])
    assert err["status"] == "error"
    assert "kaboom" in err["error"]


@pytest.mark.asyncio
async def test_log_execution_async(monkeypatch):
    created = []

    def fake_get_logger(name, internal=False):
        lg = DummyLogger(name)
        created.append(lg)
        return lg

    monkeypatch.setattr(decorators, "get_logger", fake_get_logger)

    @log_execution
    async def coro(x, token="tok"):
        await asyncio.sleep(0)
        return f"OK:{x}"

    res = await coro(7, token="secret123")
    assert res == "OK:7"

    # Find the app logger
    app_logger = next(lg for lg in created if lg.name == "app")
    assert len(app_logger.infos) == 2

    start = json.loads(app_logger.infos[0])
    assert start["status"] == "started"
    assert "secret123" not in start["kwargs"]

    done = json.loads(app_logger.infos[1])
    assert done["status"] == "completed"
    assert "OK:7" in done["result"]
