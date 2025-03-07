"""
Hestia Logger - Request Logger.

Logs HTTP request and response details for API-based applications.
Supports FastAPI, Flask, and other web frameworks.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging

# Initialize request logger
requests_logger = logging.getLogger("hestia_requests")
requests_logger.setLevel(logging.INFO)

# Add console handler
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(console_formatter)
requests_logger.addHandler(console_handler)
