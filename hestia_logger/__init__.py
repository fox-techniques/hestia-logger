"""
Hestia Logger - Asynchronous & Structured Logging System.

This package provides a high-performance, structured logging system that supports:
- Thread-based logging for performance and scalability.
- JSON and plain-text log formats.
- Internal logging for debugging Hestia Logger itself.
- Compatibility with FastAPI, Flask, standalone scripts, and microservices.
- Optional Elasticsearch integration for centralized logging.

"""

# Define public API for `hestia_logger`
__all__ = ["get_logger", "LOG_LEVEL", "ELASTICSEARCH_HOST"]

# Expose only necessary functions/classes for clean imports
from .core.custom_logger import get_logger
from .core.config import LOG_LEVEL, ELASTICSEARCH_HOST
