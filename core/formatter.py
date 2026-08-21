import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from ..config.settings import LogFormat, TimePrecision


class LogDockFormatter(logging.Formatter):
    def __init__(self, log_format: LogFormat):
        fields = []

        if log_format.time.enabled:
            fields.append("%(asctime)s")

        if log_format.app_name.enabled:
            fields.append("%(name)s")

        fields.append("%(levelname)s")

        if log_format.source.enabled:
            source_field = "%(pathname)s" if log_format.source.full_path else "%(filename)s"
            fields.append(source_field)

        fields.append("%(message)s")

        super().__init__(fmt=" | ".join(fields))
        self.time_format = log_format.time
        self.timezone = ZoneInfo(log_format.time.timezone)

    def formatTime(self, record, datefmt=None):
        log_datetime = datetime.fromtimestamp(record.created, tz=self.timezone)

        return self.format_datetime(log_datetime)

    def format_datetime(self, log_datetime: datetime) -> str:
        """Formata um datetime com as mesmas regras usadas nos registros."""

        formats = {
            TimePrecision.DAY: "%Y-%m-%d",
            TimePrecision.HOUR: "%Y-%m-%d %H",
            TimePrecision.MINUTE: "%Y-%m-%d %H:%M",
            TimePrecision.SECOND: "%Y-%m-%d %H:%M:%S",
            TimePrecision.MILLISECOND: "%Y-%m-%d %H:%M:%S.%f",
        }
        formatted_time = log_datetime.strftime(formats[self.time_format.precision])

        if self.time_format.precision is TimePrecision.MILLISECOND:
            return formatted_time[:-3]

        return formatted_time
