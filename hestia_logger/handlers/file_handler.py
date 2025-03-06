"""
Hestia Logger - Threaded File Handlers.

Ensures logs are written asynchronously using a dedicated background thread.

"""

import logging
import threading
import queue
import os
import json
from ..core.config import LOG_FILE_PATH_APP, LOG_FILE_PATH_ALL, LOG_LEVEL
from ..internal_logger import hestia_internal_logger

__all__ = ["file_handler_app", "file_handler_all"]

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH_APP), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE_PATH_ALL), exist_ok=True)


class ThreadedFileHandler(logging.Handler):
    """
    A threaded file handler that ensures logs are written asynchronously.
    """

    def __init__(self, log_file, formatter):
        super().__init__()
        self.log_file = log_file
        self.log_queue = queue.Queue()
        self.formatter = formatter
        self._stop_event = threading.Event()

        # Start a background thread to write logs
        self.worker_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.worker_thread.start()

    def _process_logs(self):
        """
        Processes logs from the queue and writes them to the file.
        """
        while not self._stop_event.is_set():
            try:
                record = self.log_queue.get(timeout=1)
                log_entry = self.format(record)
                with open(self.log_file, mode="a", encoding="utf-8") as f:
                    f.write(log_entry + "\n")
                hestia_internal_logger.debug(
                    f"Successfully wrote log to {self.log_file}."
                )
            except queue.Empty:
                continue

    def emit(self, record):
        """
        Formats log records and adds them to the queue for background writing.
        """
        hestia_internal_logger.debug(f"🔄 Queuing log for write: {record.getMessage()}")
        self.log_queue.put(record)

    def stop(self):
        """
        Stops the background thread gracefully.
        """
        self._stop_event.set()
        self.worker_thread.join()


# Apply structured formatters
json_formatter = logging.Formatter(
    json.dumps(
        {"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}
    )
)
text_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Apply `LOG_LEVEL` to handlers
file_handler_app = ThreadedFileHandler(LOG_FILE_PATH_APP, json_formatter)
file_handler_all = ThreadedFileHandler(LOG_FILE_PATH_ALL, text_formatter)
file_handler_app.setLevel(LOG_LEVEL)
file_handler_all.setLevel(LOG_LEVEL)
