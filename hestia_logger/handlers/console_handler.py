"""
Hestia Logger - Console Handler.

Defines a structured console handler that outputs logs to the terminal
with proper formatting.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging

__all__ = ["console_handler"]

# Create console handler with a standard formatter
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.DEBUG)
