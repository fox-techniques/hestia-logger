"""
Internal Logger for Hestia Package.

Logs package-related debugging messages (not user logs).

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
import os
from .core.config import LOG_FILE_PATH_INTERNAL, ENABLE_INTERNAL_LOGGER

# Internal logger instance
hestia_internal_logger = logging.getLogger("hestia_internal_logger")

if ENABLE_INTERNAL_LOGGER:
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(LOG_FILE_PATH_INTERNAL), exist_ok=True)

    # Set up internal logging
    logging.basicConfig(
        level=logging.INFO if ENABLE_INTERNAL_LOGGER else logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE_PATH_INTERNAL),
            logging.StreamHandler(),
        ],
    )

    hestia_internal_logger.info("Hestia Logger Package Initialized.")
else:
    # Disable internal logging
    hestia_internal_logger.disabled = True
