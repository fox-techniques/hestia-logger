import asyncio
from hestia_logger.core.custom_logger import get_logger
from hestia_logger.internal_logger import hestia_internal_logger
import logging

# Define service loggers (NO NEED to define `app_logger`)
logger_api = get_logger("api_service", log_level=logging.DEBUG)
logger_db = get_logger("database_service", log_level=logging.WARNING)


async def test_hestia_logging():
    """
    Logs structured messages to multiple loggers to test all log levels.
    """
    hestia_internal_logger.info("🎉 Starting Hestia Logger Test...")

    # Log structured JSON message (this will now go to `app.log` automatically)
    # logger_api.info({"message": "Main script started.", "event": "app_init"})

    # API Logger Test (DEBUG + INFO)
    logger_api.debug(
        "🐞 API Debug: Testing API request logging."
    )  # Will go to service log
    logger_api.info("📥 API Received request.")  # Will go to service log

    # Database Logger Test (WARNING + ERROR + CRITICAL)
    logger_db.warning(
        "⚠️ Database Warning: Query execution slow."
    )  # Will go to service log
    logger_db.error("❌ Database Error: Connection failed!")  # Will go to service log
    logger_db.critical(
        "🚨 CRITICAL Database Error: System Down!"
    )  # Will go to service log

    await asyncio.sleep(1)

    # Log completion message (this will now go to `app.log` automatically)
    logger_db.info({"message": "Main script completed.", "event": "app_done"})

    hestia_internal_logger.info("🏁 Hestia Logger Test Completed!")


# No need to manually flush `app.log` anymore!
asyncio.run(test_hestia_logging())

print("[DEBUG] Test script completed.")
