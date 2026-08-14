from dataclasses import dataclass
from enum import StrEnum


@dataclass
class Notification:
    enabled: bool = False
    provider: str | None = None
    chat_id: str | None = None


@dataclass
class AzureFunctionNotification(Notification):
    endpoint: str | None = None

@dataclass
class Persistence:
    enabled: bool = False
    provider: str | None = None
    connection_string: str | None = None
    container: str | None = None

class Levels(StrEnum):
    INFO: str = "INFO"
    DEBUG: str = "DEBUG"
    WARNING:str = "WARNING"
    ERROR : str = "ERROR"
    CRITIAL_ERROR : str = "CRITICAL_ERROR"

    
@dataclass
class LogDockSettings:
    app_name:str
    persistence: Persistence
    notification: Notification
    level: str = Levels.INFO