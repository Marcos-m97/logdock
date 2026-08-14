# logdock/config.py

import json
from pathlib import Path
from .settings import (
    LogDockSettings, 
    Persistence, 
    Notification, 
    Levels, 
    NotificationProvider, 
    PersistenceProvider,
    AzureFunctionNotification,
    TelegramNotification,
    AzureBlobStoragePersistence,
    )

class InvalidSettingsException(Exception):
    pass

def load_settings():
    config_path = Path.cwd() / "logdock.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        settings = json.load(file)

        app_name = settings["app_name"]

        notification_enabled=settings["notification_enabled"] 
        notification_provider=settings["notification_provider"] 
        notification_chat_id=settings["notification_chat_id"]

        persistence_enabled= settings["persistence_enabled"] 
        persistence_provider=settings["persistence_provider"] 
        persistence_connection_string=settings["persistence_connection_string"] 
        persistence_container=settings["persistence_container"] 


        log_level=str(settings["log_level"]).strip().upper() or "INFO"

        # =============================================================
        # region Notificação 

        if notification_enabled:

            try:
                notification_provider = NotificationProvider(notification_provider)
            except ValueError:
                raise InvalidSettingsException(
                    f"Notification provider inválido: '{notification_provider}'. "
                    f"Valores suportados: {[item.value for item in NotificationProvider]}"
                )

            # Instanciar notification com base no provider identificado: 
            match notification_provider:
                case NotificationProvider.AZURE_FUNCTION:
                    notification = AzureFunctionNotification(
                        enabled=True, endpoint=""
                        )

                case NotificationProvider.TELEGRAM:
                    notification = TelegramNotification(
                        enabled=True, token="", 
                        chat_id=notification_chat_id, 
                        endpoint=""
                        )

        else:
            notification = Notification()

        # =============================================================
        # region Persistencia
        
        if persistence_enabled: 

            try:
                persistence_provider = PersistenceProvider(persistence_provider)
            except ValueError:
                raise InvalidSettingsException(
                    f"Notification provider inválido: '{persistence_provider}'. "
                    f"Valores suportados: {[item.value for item in PersistenceProvider]}"
                )

            # Instanciar notification com base no provider identificado: 
            match persistence_provider:
                case PersistenceProvider.AZURE_BLOB_STORAGE:
                    persistence = AzureBlobStoragePersistence(
                        enabled=True, 
                        connection_string=persistence_connection_string, 
                        container=persistence_container
                    )

        else:
            persistence = Persistence()    

        # =============================================================
        # region Level
        
        try:
            level = Levels(log_level)
        except ValueError:
            raise InvalidSettingsException(
                f"Level invalido: '{level}'. "
                f"Valores suportados: {[item.value for item in Levels]}"
            )
        
        # =============================================================
        # region Montar setting
        
        logdock_settings = LogDockSettings(
            app_name=app_name,
            persistence=persistence,
            notification=notification,
            level=level
        )

        return logdock_settings