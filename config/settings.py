from dataclasses import dataclass, field
from enum import StrEnum
from ..integrations.telegram_client import TelegramClient

# ========================================================

class NotificationProvider(StrEnum):
    TELEGRAM = "TELEGRAM"
    AZURE_FUNCTION = "AZURE_FUNCTION"

@dataclass
class Notification:
    enabled: bool = False
    provider: NotificationProvider | None = None

@dataclass
class AzureFunctionNotification(Notification):
    endpoint: str | None = None
    function_key: str | None = None

@dataclass
class TelegramNotification(Notification):
    token: str | None = None
    chat_id: str | None = None

# ========================================================
class PersistenceProvider(StrEnum):
    AZURE_BLOB_STORAGE = "AZURE_BLOB_STORAGE"
  
@dataclass
class Persistence:
    enabled: bool = False

@dataclass
class AzureBlobStoragePersistence(Persistence):
    connection_string: str | None = None
    container: str | None = None

# ========================================================
class Levels(StrEnum):
    INFO: str = "INFO"
    DEBUG: str = "DEBUG"


class TimePrecision(StrEnum):
    DAY = "DAY"
    HOUR = "HOUR"
    MINUTE = "MINUTE"
    SECOND = "SECOND"
    MILLISECOND = "MILLISECOND"


@dataclass
class LogTimeFormat:
    enabled: bool = False
    timezone: str = "UTC"
    precision: TimePrecision = TimePrecision.SECOND


@dataclass
class AppNameFormat:
    enabled: bool = False


@dataclass
class SourceFormat:
    enabled: bool = False
    full_path: bool = False


@dataclass
class LogFormat:
    time: LogTimeFormat = field(default_factory=LogTimeFormat)
    app_name: AppNameFormat = field(default_factory=AppNameFormat)
    source: SourceFormat = field(default_factory=SourceFormat)


# ========================================================
@dataclass
class LogDockSettings:
    app_name:str
    persistence: Persistence
    notification: Notification
    log_format: LogFormat = field(default_factory=LogFormat)
    level: str = Levels.INFO

@dataclass
class LogDockIntegrations:
    telegram_client: TelegramClient | None = None
    azure_functions_client : str | None = None
    azure_blob_storage_client : str | None = None

