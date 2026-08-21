import logging
from threading import Lock

from ..config.settings import LogFormat
from .formatter import LogDockFormatter


class LogBufferHandler(logging.Handler):
    def __init__(self, execution_id: str, log_format: LogFormat):
        super().__init__(level=logging.NOTSET)
        self.execution_id = execution_id
        self.log_format = log_format
        self.log_formatter = LogDockFormatter(log_format)
        self._records: list[dict] = []
        self._records_lock = Lock()

    def emit(self, record: logging.LogRecord) -> None:
        if getattr(record, "logdock_execution_id", None) != self.execution_id:
            return

        item = {}
        if self.log_format.time.enabled:
            item["timestamp"] = self.log_formatter.formatTime(record)
        item["level"] = record.levelname

        if self.log_format.source.enabled:
            item["source"] = (
                record.pathname
                if self.log_format.source.full_path
                else record.filename
            )

        item["message"] = record.getMessage()
        with self._records_lock:
            self._records.append(item)

    def snapshot(self) -> list[dict]:
        with self._records_lock:
            return [record.copy() for record in self._records]

    def discard(self, count: int) -> None:
        with self._records_lock:
            del self._records[:count]
