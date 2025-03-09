# test_config.py

import os
import logging
import socket
import pytest
import importlib
from hestia_logger.core import config


def test_default_environment(monkeypatch):
    # Ensure ENVIRONMENT defaults to "local"
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    importlib.reload(config)
    assert config.ENVIRONMENT == "local"


def test_custom_environment(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    importlib.reload(config)
    assert config.ENVIRONMENT == "production"  # lowercased in config


def test_log_level_default(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    importlib.reload(config)
    # Default LOG_LEVEL is INFO
    assert config.LOG_LEVEL == logging.INFO


def test_log_level_debug(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    importlib.reload(config)
    assert config.LOG_LEVEL == logging.DEBUG


def test_elasticsearch_host(monkeypatch):
    # Test default value is empty string
    monkeypatch.delenv("ELASTICSEARCH_HOST", raising=False)
    importlib.reload(config)
    assert config.ELASTICSEARCH_HOST == ""
    # Test custom value
    monkeypatch.setenv("ELASTICSEARCH_HOST", "http://localhost:9200")
    importlib.reload(config)
    assert config.ELASTICSEARCH_HOST == "http://localhost:9200"


def test_enable_internal_logger(monkeypatch):
    monkeypatch.setenv("ENABLE_INTERNAL_LOGGER", "true")
    importlib.reload(config)
    assert config.ENABLE_INTERNAL_LOGGER is True
    monkeypatch.setenv("ENABLE_INTERNAL_LOGGER", "false")
    importlib.reload(config)
    assert config.ENABLE_INTERNAL_LOGGER is False


def test_logs_dir(monkeypatch, tmp_path):
    # Test when LOGS_DIR is not set; expect local logs directory
    monkeypatch.delenv("LOGS_DIR", raising=False)
    # Set current working directory to tmp_path to control the expected logs dir.
    monkeypatch.chdir(tmp_path)
    importlib.reload(config)
    expected_logs_dir = str(tmp_path / "logs")
    assert config.LOGS_DIR == expected_logs_dir

    # Test when LOGS_DIR is explicitly set.
    custom_logs = str(tmp_path / "custom_logs")
    monkeypatch.setenv("LOGS_DIR", custom_logs)
    importlib.reload(config)
    assert config.LOGS_DIR == custom_logs


def test_log_file_paths(monkeypatch, tmp_path):
    # Force LOGS_DIR to a temporary directory
    monkeypatch.setenv("LOGS_DIR", str(tmp_path / "logs"))
    importlib.reload(config)
    # Verify that log file paths end with the correct filenames.
    assert config.LOG_FILE_PATH_APP.endswith("app.log")
    assert config.LOG_FILE_PATH_INTERNAL.endswith("hestia_logger_internal.log")


def test_hostname():
    # HOSTNAME should be a non-empty string.
    assert isinstance(config.HOSTNAME, str) and config.HOSTNAME != ""


def test_detect_container(monkeypatch):
    # Simulate container environment by faking file existence.
    monkeypatch.setattr(
        os.path, "exists", lambda path: True if path == "/.dockerenv" else False
    )
    # For container simulation, force reading of container data.
    monkeypatch.setattr(config, "IS_CONTAINER", True)
    importlib.reload(config)
    assert config.IS_CONTAINER is True


def test_container_logs_dir(monkeypatch):
    # Simulate container environment so that default LOGS_DIR should be /logs.
    monkeypatch.setattr(
        os.path, "exists", lambda path: True if path == "/.dockerenv" else False
    )
    monkeypatch.setenv("LOGS_DIR", "")
    importlib.reload(config)
    assert config.LOGS_DIR == "/logs"
