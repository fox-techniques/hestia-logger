"""
Logging Configuration.

Features:
- Defines log levels, log format, and log storage locations dynamically.
- Supports structured JSON logging for applications.
- Logs container ID and hostname for observability.
- Environment-based configurations (local vs container).
- Cloud-ready (Elasticsearch, Azure Log Analytics).

Environment Variables:
- ENVIRONMENT: `local` (default) or `container` (changes log directory to `/var/logs`).
- LOG_LEVEL: Must be explicitly set (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- LOG_FORMAT: `JSON` (default) or `TEXT` for structured vs human-readable logs.
- ELASTICSEARCH_HOST: (Optional) Elasticsearch endpoint for log forwarding.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import socket
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Detect environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "local").lower()
IS_CONTAINER = (
    os.path.exists("/proc/1/cgroup") and "docker" in open("/proc/1/cgroup").read()
)

# Get system identifiers
HOSTNAME = socket.gethostname()
CONTAINER_ID = (
    open("/proc/self/cgroup").read().splitlines()[-1].split("/")[-1]
    if IS_CONTAINER
    else "N/A"
)

# Define log directory
LOGS_DIR = "/var/logs" if IS_CONTAINER else os.path.join(os.getcwd(), "logs")

# Ensure log directory exists before logging starts
os.makedirs(LOGS_DIR, exist_ok=True)

# Define log file paths
LOG_FILE_PATH_APP = os.path.join(LOGS_DIR, "app.log")
LOG_FILE_PATH_ALL = os.path.join(LOGS_DIR, "all.log")

# Read log settings from environment and enforce explicit `LOG_LEVEL`
LOG_LEVEL = os.getenv("LOG_LEVEL")
if not LOG_LEVEL:
    raise ValueError("LOG_LEVEL must be set in the environment variables.")
LOG_LEVEL = LOG_LEVEL.upper()

# Read log format (JSON or TEXT) from environment
LOG_FORMAT = os.getenv("LOG_FORMAT", "JSON").upper()

# Read Elasticsearch host if provided
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "").strip()

# Debugging prints (optional, for troubleshooting)
print(f"🔍 ENVIRONMENT: {ENVIRONMENT}")
print(f"🔍 LOG_LEVEL: {LOG_LEVEL}")
print(f"🔍 LOG_FORMAT: {LOG_FORMAT}")
print(f"🔍 LOGS_DIR: {LOGS_DIR}")
print(
    f"🔍 ELASTICSEARCH_HOST: {ELASTICSEARCH_HOST if ELASTICSEARCH_HOST else 'Not Configured'}"
)
