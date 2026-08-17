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

        app_name = settings["app_name"]                                                 # Nome do app

        notification_enabled = settings["notification_enabled"]                           # Notificação habilitada | desabilitada
        notification_provider = settings["notification_provider"]                         # Provider de notificação 
        notification_endpoint = settings["notification_endpoint"]

        notification_telegram_token = settings["notification_telegram_token"]
        notification_telegram_chat_id = settings["notification_telegram_chat_id"]

        persistence_enabled = settings["persistence_enabled"] 
        persistence_provider = settings["persistence_provider"]

        persistence_blob_connection_string = settings["persistence_blob_connection_string"] 
        persistence_blob_container = settings["persistence_blob_container"] 

        log_level=str(settings["log_level"]).strip().upper() or "INFO"

        # =============================================================
        # region Notificação 

        if notification_enabled:

            # Validação de providers suportados
            try:
                # NotificationProvider é um strEnum com os providers suportados
                # ao instanciar a classe se ela não estiver cadastrada volta value error
                notification_provider = NotificationProvider(notification_provider)
            except ValueError:
                raise InvalidSettingsException(
                    f"Notification provider inválido: '{notification_provider}'. "
                    f"Valores suportados: {[item.value for item in NotificationProvider]}"
                )

            # Instanciar notification com base no provider identificado: 
            # as settings finais vão carregar em notification a instancia 
            # do provider configurado no json de settings.
            # Depois o método notify() do core verifica a instancia recebida para utilizar os dados corretos
            match notification_provider:
                case NotificationProvider.AZURE_FUNCTION:
                    notification = AzureFunctionNotification(
                        enabled=True,
                        provider=NotificationProvider.AZURE_FUNCTION,
                        endpoint=notification_endpoint
                        )

                case NotificationProvider.TELEGRAM:
                    notification = TelegramNotification(
                        enabled=True,
                        provider=NotificationProvider.TELEGRAM, 
                        token=notification_telegram_token, 
                        chat_id=notification_telegram_chat_id
                        )

        else:
            # Caso notificação esteja desabilitado, notification recebe a classe base que contém
            # apenas enabled = False
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
                        connection_string=persistence_blob_connection_string, 
                        container=persistence_blob_container
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
        # region Montar setting final
        logdock_settings = LogDockSettings(
            app_name=app_name,
            persistence=persistence,
            notification=notification,
            level=level
        )

        return logdock_settings