from ..config.settings import (
    AzureBlobStoragePersistence,
    AzureFunctionNotification,
    LocalPersistence,
    LogDockIntegrations,
    LogDockSettings,
    TelegramNotification,
)
from ..integrations.persistence import (
    AzureBlobPersistenceClient,
    LocalPersistenceClient,
)
from ..integrations.telegram_client import TelegramClient


def register_integrations(logdock_settings: LogDockSettings) -> LogDockIntegrations:
    telegram_client = None
    azure_functions_client = None
    persistence_client = None

    if logdock_settings.notification.enabled:
        notification = logdock_settings.notification

        if isinstance(notification, TelegramNotification):
            telegram_client = TelegramClient(
                token=notification.token,
                chat_id=notification.chat_id,
            )
        elif isinstance(notification, AzureFunctionNotification):
            # Cliente da Azure Function ainda não foi implementado.
            azure_functions_client = notification.endpoint

    if logdock_settings.persistence.enabled:
        persistence = logdock_settings.persistence

        if isinstance(persistence, LocalPersistence):
            persistence_client = LocalPersistenceClient(path=persistence.path)
        elif isinstance(persistence, AzureBlobStoragePersistence):
            persistence_client = AzureBlobPersistenceClient(
                connection_string=persistence.connection_string,
                container=persistence.container,
            )

    return LogDockIntegrations(
        telegram_client=telegram_client,
        azure_functions_client=azure_functions_client,
        persistence_client=persistence_client,
    )
