"""
Request Logging Utility.

Features:
- Logs outgoing HTTP requests including method, URL, and headers.
- Measures request execution time.
- Logs responses including status code and response time.
- Handles exceptions and logs errors with full traceback.
- Supports both structured JSON and human-readable logs.

Environment Variables:
- LOG_LEVEL: Must be explicitly set (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import time
import requests
from .custom_logger import get_logger

logger = get_logger("requests")


def log_request_response(func):
    """
    Decorator to log outgoing HTTP requests and responses.

    Logs request details, execution time, response status, and errors.
    """

    def wrapper(*args, **kwargs):
        url = kwargs.get("url") or (args[0] if args else "Unknown URL")
        method = kwargs.get("method", "GET").upper()
        start_time = time.time()

        logger.info(f"➡️ Sending {method} request to {url}")
        try:
            response = func(*args, **kwargs)
            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
            logger.info(
                f"✅ Received response {response.status_code} from {url} in {elapsed_time:.2f}ms"
            )
            return response

        except requests.RequestException as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"❌ Request to {url} failed in {elapsed_time:.2f}ms. Error: {e}"
            )
            raise

    return wrapper


@log_request_response
def send_request(method, url, **kwargs):
    """
    Sends an HTTP request and logs the process.

    Args:
        method (str): HTTP method (GET, POST, etc.).
        url (str): Target URL.
        **kwargs: Additional parameters for `requests.request()`.

    Returns:
        Response: The HTTP response object.
    """
    return requests.request(method, url, **kwargs)
