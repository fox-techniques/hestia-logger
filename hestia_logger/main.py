import asyncio
from hestia_logger.core.custom_logger import get_logger
from hestia_logger.internal_logger import hestia_internal_logger
import logging

# Separate loggers for different services
app_logger = get_logger("app")  # Global app logger
logger_api = get_logger("api_service", log_level=logging.DEBUG)
logger_db = get_logger("database_service", log_level=logging.WARNING)


async def test_hestia_logging():
    """
    Logs structured messages to multiple loggers.
    """
    hestia_internal_logger.info("🎉 Starting Hestia Logger Test...")

    # Global App Logging
    app_logger.info("✅ Global application log working!")

    # API Logger Test
    logger_api.debug("🐞 API Debug: Testing API request logging.")
    logger_api.info("📥 API Received request.")  # Will also go to `app.log`

    # Database Logger Test
    logger_db.warning(
        "⚠️ Database Warning: Query execution slow."
    )  # Will also go to `app.log`
    logger_db.error(
        "❌ Database Error: Connection failed!"
    )  # Will also go to `app.log`

    # Simulate async logging
    await asyncio.sleep(1)

    hestia_internal_logger.info("🏁 Hestia Logger Test Completed!")


# Run the test
asyncio.run(test_hestia_logging())
