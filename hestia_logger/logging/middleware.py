"""
Logging Middleware.

Features:
- Logs every incoming HTTP request and its response status.
- Generates and attaches a unique request ID for traceability.
- Measures and logs request execution time.
- Handles errors and logs detailed exceptions.
- Supports both structured JSON and human-readable logs.

Environment Variables:
- LOG_LEVEL: Must be explicitly set (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import time
import logging
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .custom_logger import get_logger

logger = get_logger("middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log HTTP requests and responses.

    Logs request method, URL, execution time, and response status.
    Adds a unique request ID to each request for tracing purposes.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(
            f"➡️ Request {request_id} started: {request.method} {request.url.path}"
        )

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            logger.info(
                f"✅ Request {request_id} completed in {process_time:.2f}ms with status {response.status_code}"
            )
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"❌ Request {request_id} failed in {process_time:.2f}ms. Error: {e}"
            )
            raise
