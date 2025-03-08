import asyncio
from hestia_logger.core.custom_logger import get_logger
from hestia_logger.internal_logger import hestia_internal_logger
import logging

# Separate loggers for different services
logger_api = get_logger("api_service", log_level=logging.DEBUG)
logger_db = get_logger("database_service", log_level=logging.WARNING)


async def test_hestia_logging():
    """
    Logs structured messages to multiple loggers to test all log levels.
    """
    hestia_internal_logger.info("🎉 Starting Hestia Logger Test...")

    # API Logger Test (DEBUG + INFO)
    logger_api.debug(
        "🐞 API Debug: Testing API request logging."
    )  # ✅ Should appear in `app.log`
    logger_api.info("📥 API Received request.")  # ✅ Should appear in `app.log`

    # Database Logger Test (WARNING + ERROR + CRITICAL)
    logger_db.warning(
        "⚠️ Database Warning: Query execution slow."
    )  # ✅ Should appear in `app.log`
    logger_db.error(
        "❌ Database Error: Connection failed!"
    )  # ✅ Should appear in `app.log`
    logger_db.critical(
        "🚨 CRITICAL Database Error: System Down!"
    )  # ✅ Should appear in `app.log`

    # Simulate async logging
    await asyncio.sleep(1)

    hestia_internal_logger.info("🏁 Hestia Logger Test Completed!")


# Run the test
asyncio.run(test_hestia_logging())
