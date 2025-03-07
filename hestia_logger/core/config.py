"""
Hestia Logger - Configuration Module.

Defines environment-based logging settings for Hestia Logger.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import socket
import logging
from dotenv import load_dotenv

# Load environment variables from `.env` file
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

# Ensure log directory exists
LOGS_DIR = (
    "/var/logs" if ENVIRONMENT == "container" else os.path.join(os.getcwd(), "logs")
)
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE_PATH_APP = os.path.join(LOGS_DIR, "app.log")
# LOG_FILE_PATH_ALL = os.path.join(LOGS_DIR, "all.log")
LOG_FILE_PATH_INTERNAL = os.path.join(LOGS_DIR, "hestia_logger_internal.log")

# Safe Conversion of `LOG_LEVEL`
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL = LOG_LEVELS.get(
    LOG_LEVEL_STR, logging.INFO
)  # Convert string to logging constant

# Apply LOG_LEVEL globally to the root logger
logging.basicConfig(level=LOG_LEVEL, force=True)
logging.root.setLevel(LOG_LEVEL)

# Read Elasticsearch host if provided
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "").strip()

# Enable or Disable Internal Logging
ENABLE_INTERNAL_LOGGER = os.getenv("ENABLE_INTERNAL_LOGGER", "false").lower() == "true"

# Log Rotation Settings
LOG_ROTATION_TYPE = os.getenv("LOG_ROTATION_TYPE", "size")  # "size" or "time"
LOG_ROTATION_WHEN = os.getenv(
    "LOG_ROTATION_WHEN", "midnight"
)  # Only for time-based rotation
LOG_ROTATION_INTERVAL = int(
    os.getenv("LOG_ROTATION_INTERVAL", 1)
)  # Interval for time-based rotation
LOG_ROTATION_BACKUP_COUNT = int(
    os.getenv("LOG_ROTATION_BACKUP_COUNT", 5)
)  # Keep last 5 log files
LOG_ROTATION_MAX_BYTES = int(
    os.getenv("LOG_ROTATION_MAX_BYTES", 10 * 1024 * 1024)
)  # 10 MB max per log file
