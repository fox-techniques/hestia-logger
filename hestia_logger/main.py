"""
Main Test Script for Hestia Logger.

- Verifies both structured logging and internal debugging logs.
- Ensures logs appear in console, `app.log`, and `hestia_logger_internal.log`.
- Simulates errors to check logging system resilience.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import asyncio
import os
from hestia_logger.core.custom_logger import get_logger
from hestia_logger.internal_logger import hestia_internal_logger

# Get an async logger instance for application logs
app_logger = get_logger("hestia_test")


async def test_hestia_logging():
    """
    Logs structured messages and verifies logging functionality.
    """
    hestia_internal_logger.info("🎉 Starting Hestia Logger Test...")

    # Log messages using Hestia’s structured logger
    app_logger.info("✅ Hestia structured logging is working!")
    app_logger.debug("🐞 Debug: This is a test debug message.")
    app_logger.warning("🔔 Warning: This is a test warning message.")
    app_logger.error("❌ Error: Something went wrong!")
    app_logger.critical("🚨 Critical: System is down!")

    # Simulate an internal error for debugging
    try:
        1 / 0  # Intentional division by zero
    except ZeroDivisionError as e:
        hestia_internal_logger.error(f"❌ Internal error occurred: {e}")

    # Allow async file writes to complete before checking logs
    hestia_internal_logger.info("⏳ Waiting for logs to be written...")
    await asyncio.sleep(2)

    # Check logs folder
    hestia_internal_logger.info("🔍 Checking logs directory:")
    os.system("ls -l logs/")

    # Check if `app.log` exists
    if os.path.exists("logs/app.log"):
        hestia_internal_logger.info("✅ app.log exists.")
        if os.path.getsize("logs/app.log") > 0:
            hestia_internal_logger.info("✅ app.log contains logs.")
        else:
            hestia_internal_logger.error("❌ app.log is empty!")
    else:
        hestia_internal_logger.error("❌ app.log does NOT exist!")

    # Check if `hestia_logger_internal.log` exists
    if os.path.exists("logs/hestia_logger_internal.log"):
        hestia_internal_logger.info("✅ Internal logger log file exists.")
        if os.path.getsize("logs/hestia_logger_internal.log") > 0:
            hestia_internal_logger.info("✅ Internal logger contains logs.")
        else:
            hestia_internal_logger.error("❌ Internal logger file is empty!")
    else:
        hestia_internal_logger.error("❌ Internal logger file does NOT exist!")

    # Check if `app.log` exists
    if os.path.exists("logs/app.log"):
        hestia_internal_logger.info("✅ Application log file exists.")
        if os.path.getsize("logs/app.log") > 0:
            hestia_internal_logger.info("✅ Application logger contains logs.")
        else:
            hestia_internal_logger.error("❌ Application logger file is empty!")
    else:
        hestia_internal_logger.error("❌ Application logger file does NOT exist!")

    # Check if `all.log` exists
    if os.path.exists("logs/all.log"):
        hestia_internal_logger.info("✅ Human-readable log file exists.")
        if os.path.getsize("logs/all.log") > 0:
            hestia_internal_logger.info("✅ Human-readable logger contains logs.")
        else:
            hestia_internal_logger.error("❌ Human-readable log file is empty!")
    else:
        hestia_internal_logger.error("❌ Human-readable log file does NOT exist!")

    hestia_internal_logger.info("🏁 Hestia Logger Test Completed!")


# Run the test
asyncio.run(test_hestia_logging())
