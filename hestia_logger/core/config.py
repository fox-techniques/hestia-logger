"""
Logging Configuration.

This module defines environment-based logging settings for the application.

Features:
- Dynamically determines log level and format.
- Supports structured JSON logging.
- Detects whether the app is running in a container (Docker/Kubernetes).
- Configures Elasticsearch logging if enabled.
- Defines log storage paths based on environment.
- Allows enabling/disabling internal logger for package debugging.

Environment Variables:
- ENVIRONMENT: `local` (default) or `container` (changes log directory to `/var/logs`).
- LOG_LEVEL: Must be explicitly set (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- LOG_FORMAT: `JSON` (default) or `TEXT` for structured vs human-readable logs.
- ELASTICSEARCH_HOST: (Optional) Elasticsearch endpoint for cloud log forwarding.
- HESTIA_INTERNAL_LOGGER: `true` (default) or `false` to disable internal logs.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import socket
from dotenv import load_dotenv

# Load environment variables from `.env` file if present
load_dotenv()

# Detect runtime environment (local or container)
ENVIRONMENT = os.getenv("ENVIRONMENT", "local").lower()
IS_CONTAINER = (
    os.path.exists("/proc/1/cgroup") and "docker" in open("/proc/1/cgroup").read()
)

# Retrieve system identifiers
HOSTNAME = socket.gethostname()
CONTAINER_ID = (
    open("/proc/self/cgroup").read().splitlines()[-1].split("/")[-1]
    if IS_CONTAINER
    else "N/A"
)

# Ensure log directory exists before logging starts
LOGS_DIR = (
    "/var/logs"
    if os.getenv("ENVIRONMENT", "local").lower() == "container"
    else os.path.join(os.getcwd(), "logs")
)
os.makedirs(LOGS_DIR, exist_ok=True)  # Ensures directory exists

LOG_FILE_PATH_APP = os.path.join(LOGS_DIR, "app.log")
LOG_FILE_PATH_ALL = os.path.join(LOGS_DIR, "all.log")
LOG_FILE_PATH_INTERNAL = os.path.join(LOGS_DIR, "hestia_logger_internal.log")

# Read log level from environment variables
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
if LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    raise ValueError(
        f"Invalid LOG_LEVEL: {LOG_LEVEL}. Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL."
    )

# Read log format (JSON or TEXT) from environment
LOG_FORMAT = os.getenv("LOG_FORMAT", "JSON").upper()
if LOG_FORMAT not in {"JSON", "TEXT"}:
    raise ValueError(f"Invalid LOG_FORMAT: {LOG_FORMAT}. Must be JSON or TEXT.")

# Read Elasticsearch host if provided
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "").strip()

# Enable or Disable Internal Logging
ENABLE_INTERNAL_LOGGER = os.getenv("ENABLE_INTERNAL_LOGGER", "true").lower() == "true"

# Import internal logger only if enabled
if ENABLE_INTERNAL_LOGGER:
    from ..internal_logger import hestia_internal_logger

    # Debugging prints (only if internal logger is enabled)
    hestia_internal_logger.debug(f"🔍 ENVIRONMENT: {ENVIRONMENT}")
    hestia_internal_logger.debug(f"🔍 LOG_LEVEL: {LOG_LEVEL}")
    hestia_internal_logger.debug(f"🔍 LOG_FORMAT: {LOG_FORMAT}")
    hestia_internal_logger.debug(f"🔍 LOGS_DIR: {LOGS_DIR}")
    hestia_internal_logger.debug(
        f"🔍 ELASTICSEARCH_HOST: {ELASTICSEARCH_HOST if ELASTICSEARCH_HOST else 'Not Configured'}"
    )
