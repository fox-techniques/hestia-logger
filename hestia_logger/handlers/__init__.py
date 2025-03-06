"""
Hestia Logger - Handlers Module.

Defines threaded log handlers for asynchronous file-based logging,
console logging, and optional Elasticsearch logging.

"""

# Define public API for `handlers`
__all__ = ["file_handler_app", "file_handler_all", "console_handler", "es_handler"]

# Expose handlers
from .file_handler import file_handler_app, file_handler_all
from .console_handler import console_handler
from .elasticsearch_handler import es_handler  # Ensure this exists
