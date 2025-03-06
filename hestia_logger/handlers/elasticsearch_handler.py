"""
Hestia Logger - Elasticsearch Handler.

Provides optional integration with Elasticsearch for centralized logging.

Requires:
- The `elasticsearch` Python package.
- A valid Elasticsearch endpoint in `ELASTICSEARCH_HOST`.

"""

import logging
import json
from ..core.config import ELASTICSEARCH_HOST
from ..internal_logger import hestia_internal_logger

__all__ = ["es_handler"]

try:
    from elasticsearch import Elasticsearch

    class ElasticsearchHandler(logging.Handler):
        """
        Elasticsearch log handler that sends structured log events to an Elasticsearch cluster.
        """

        def __init__(self, index="hestia-logs"):
            super().__init__()
            self.index = index
            self.es = (
                Elasticsearch([ELASTICSEARCH_HOST]) if ELASTICSEARCH_HOST else None
            )

        def emit(self, record):
            """
            Sends log events to Elasticsearch.
            """
            if not self.es:
                return  # Elasticsearch is disabled

            log_entry = self.format(record)
            try:
                self.es.index(index=self.index, body=json.loads(log_entry))
                hestia_internal_logger.debug(
                    f"Successfully sent log to Elasticsearch index: {self.index}"
                )
            except Exception as e:
                hestia_internal_logger.error(
                    f"❌ ERROR SENDING LOG TO ELASTICSEARCH: {e}"
                )

    es_handler = ElasticsearchHandler() if ELASTICSEARCH_HOST else None

except ImportError:
    hestia_internal_logger.warning(
        "⚠️ Elasticsearch is not installed. Disabling Elasticsearch logging."
    )
    es_handler = None  # Prevent import errors when Elasticsearch is missing
