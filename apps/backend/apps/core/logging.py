"""Custom logging formatters with request ID support."""

import logging
import threading

_local = threading.local()


def get_request_id():
    """Get the current request ID from thread-local storage."""
    return getattr(_local, "request_id", "no-request")


def set_request_id(request_id):
    """Set the request ID for the current thread."""
    _local.request_id = request_id


class RequestIDFilter(logging.Filter):
    """Logging filter that adds request ID to log records."""

    def filter(self, record):
        """Add request_id to the log record."""
        record.request_id = get_request_id()
        return True


class RequestIDFormatter(logging.Formatter):
    """Custom formatter that includes request ID in log messages."""

    def format(self, record):
        """Format log record with request ID."""
        if not hasattr(record, "request_id"):
            record.request_id = get_request_id()
        return super().format(record)
