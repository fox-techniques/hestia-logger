"""
Async Requests Logger.

This module provides non-blocking logging for outgoing HTTP requests.

Features:
- Uses `httpx` for async HTTP calls instead of `requests`.
- Logs request method, URL, headers, and execution time.
- Captures response status and response time asynchronously.
- Uses `structlog` for structured logging.
- Ensures non-blocking execution for FastAPI applications.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import time
import httpx
from structlog import get_logger

logger = get_logger("requests")


async def log_request_response(response: httpx.Response):
    """
    Asynchronously logs HTTP request and response details.

    Args:
        response (httpx.Response): The response object.
    """
    request = response.request
    elapsed_time = response.elapsed.total_seconds() * 1000  # Convert to ms

    await logger.info(
        "✅ HTTP Request Completed",
        method=request.method,
        url=str(request.url),
        status=response.status_code,
        elapsed_time=f"{elapsed_time:.2f}ms",
    )


async def async_http_request(method: str, url: str, **kwargs):
    """
    Makes an async HTTP request using `httpx` and logs the response.

    Args:
        method (str): HTTP method (GET, POST, etc.).
        url (str): The request URL.
        **kwargs: Additional request parameters.

    Returns:
        httpx.Response: The response object.
    """
    async with httpx.AsyncClient() as client:
        start_time = time.time()

        try:
            response = await client.request(method, url, **kwargs)
            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

            await logger.info(
                "✅ HTTP Request Success",
                method=method,
                url=url,
                status=response.status_code,
                elapsed_time=f"{elapsed_time:.2f}ms",
            )
            return response

        except httpx.HTTPError as e:
            elapsed_time = (time.time() - start_time) * 1000

            await logger.error(
                "❌ HTTP Request Failed",
                method=method,
                url=url,
                error=str(e),
                elapsed_time=f"{elapsed_time:.2f}ms",
            )
            raise


async def enable_request_logging():
    """
    Enables automatic logging for all outgoing HTTP requests made with `httpx`.
    """
    async_client = httpx.AsyncClient()

    if async_client.event_hooks is None:
        async_client.event_hooks = {"response": []}  # Ensure hooks are initialized

    async_client.event_hooks["response"].append(log_request_response)
