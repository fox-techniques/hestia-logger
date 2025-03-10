# test_console_handler.py

import logging
import pytest
from hestia_logger.handlers.console_handler import console_handler


def test_console_handler_instance():
    """Test that console_handler is an instance of StreamHandler."""
    assert isinstance(
        console_handler, logging.StreamHandler
    ), "console_handler should be a StreamHandler"


def test_console_handler_formatter():
    """
    Test that after apply_logging_settings() is called,
    the console_handler's formatter is a standard Formatter with the expected format.
    """
    formatter = console_handler.formatter
    # The apply_logging_settings() in custom_logger.py resets the formatter to this:
    expected_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    assert (
        formatter._fmt == expected_format
    ), "Formatter format string does not match expected value"


def test_console_handler_level():
    """Test that the console_handler's level is set to DEBUG."""
    assert (
        console_handler.level == logging.DEBUG
    ), "console_handler level should be DEBUG"
