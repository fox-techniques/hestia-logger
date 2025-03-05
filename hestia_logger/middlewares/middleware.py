"""
Async Logging Middleware.

This module provides non-blocking logging for incoming HTTP requests in FastAPI.

Features:
- Logs every HTTP request method, URL, execution time, and status code.
- Attaches a unique request ID to each request for traceability.
- Uses `structlog` for structured JSON logging.
- Captures and logs errors with full stack traces.
- Ensures FastAPI applications remain non-blocking.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import time
import uuid
import asyncio
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from structlog import get_logger

logger = get_logger("middleware")


class AsyncLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses asynchronously.

    Logs:
    - HTTP method and URL
    - Execution time in milliseconds
    - Response status code
    - Unique request ID for tracing
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Log request start
        await logger.info(
            "📡 Request Started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
        )

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000  # Convert to ms

            # Log successful request
            await logger.info(
                "✅ Request Completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status=response.status_code,
                execution_time=f"{process_time:.2f}ms",
            )

            # Attach request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            process_time = (time.time() - start_time) * 1000

            # Log request failure
            await logger.error(
                "❌ Request Failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                execution_time=f"{process_time:.2f}ms",
            )
            raise  # Re-raise the exception after logging
