"""
Elasticsearch Log Handler.

This module provides an async handler for logging to Elasticsearch.

Features:
- Uses `AsyncElasticsearch` for non-blocking log ingestion.
- Ensures fast and structured logging for cloud observability.
- Supports JSON log format for Elasticsearch indexing.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
import asyncio
from elasticsearch import AsyncElasticsearch
from ..core.config import ELASTICSEARCH_HOST, LOG_LEVEL
from ..internal_logger import hestia_internal_logger


class AsyncElasticsearchHandler(logging.Handler):
    """
    Asynchronous Elasticsearch log handler.

    Sends logs to an Elasticsearch cluster asynchronously.
    """

    def __init__(self, host):
        super().__init__()
        self.es = AsyncElasticsearch([host])

    async def _send_log(self, log_entry):
        """Sends logs to Elasticsearch asynchronously."""
        try:
            await self.es.index(index="application-logs", body=log_entry)
        except Exception as e:
            hestia_internal_logger.error(f"🚨 Failed to send log to Elasticsearch: {e}")

    def emit(self, record):
        """Formats and sends logs asynchronously to Elasticsearch."""
        log_entry = self.format(record)
        asyncio.create_task(self._send_log(log_entry))


# Define Elasticsearch handler
es_handler = None
if ELASTICSEARCH_HOST:
    es_handler = AsyncElasticsearchHandler(ELASTICSEARCH_HOST)
    es_handler.setLevel(LOG_LEVEL)
