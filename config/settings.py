from dataclasses import dataclass
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

# ========================================================
@dataclass
class LogDockSettings:
    app_name:str
    persistence: Persistence
    notification: Notification
    level: str = Levels.INFO

@dataclass
class LogDockIntegrations:
    telegram_client: TelegramClient | None = None
    azure_functions_client : str | None = None
    azure_blob_storage_client : str | None = None

