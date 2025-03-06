"""
Hestia Logger - Logging Middleware.

Provides middleware functions for logging request and response details
in web applications using FastAPI, Flask, and other frameworks.

"""

import logging

__all__ = ["middleware"]


class LoggingMiddleware:
    """
    Middleware that logs incoming requests and outgoing responses.
    """

    def __init__(self, logger_name="hestia_middleware"):
        """
        Initializes the middleware with a logger instance.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def log_request(self, request):
        """
        Logs details of an incoming HTTP request.
        """
        self.logger.info(f"📥 Incoming Request: {request.method} {request.url}")

    def log_response(self, response):
        """
        Logs details of an outgoing HTTP response.
        """
        self.logger.info(f"📤 Outgoing Response: {response.status_code}")
