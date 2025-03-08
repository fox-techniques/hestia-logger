from hestia_logger.decorators.decorators import log_execution
from hestia_logger.core.custom_logger import get_logger
import asyncio

# ✅ Define the correct logger name explicitly
my_service_logger = get_logger("my_service")


@log_execution
def sync_function(x, y, password="12345"):
    """
    A simple synchronous function to test logging.
    """
    my_service_logger.info("Inside sync_function.")
    return x + y


@log_execution
async def async_function(x, y, token="abc123"):
    """
    A simple async function to test logging.
    """
    my_service_logger.info("Inside async_function.")
    await asyncio.sleep(1)
    return x * y


if __name__ == "__main__":
    print("Running sync test...")
    result_sync = sync_function(5, 10, password="my_secret")
    print(f"Sync result: {result_sync}")

    print("\nRunning async test...")
    result_async = asyncio.run(async_function(2, 3, token="super_secret_token"))
    print(f"Async result: {result_async}")
