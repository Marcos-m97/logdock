# logdock/config.py

import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
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
    LogFormat,
    LogTimeFormat,
    AppNameFormat,
    SourceFormat,
    TimePrecision,
    )

class InvalidSettingsException(Exception):
    pass

# =============================================================================

def _required_env(name: str) -> str:
    """
    Valida variáveis
    """
    value = os.getenv(name)

    if value is None or not value.strip():
        raise InvalidSettingsException(
            f"Variável de ambiente obrigatória não configurada: {name}"
        )

    return value.strip()

# =============================================================================

def _required_bool(settings: dict, name: str, default: bool = False) -> bool:
    value = settings.get(name, default)

    if not isinstance(value, bool):
        raise InvalidSettingsException(f"'{name}' deve ser true ou false.")

    return value


def _load_time_format(log_format: dict) -> LogTimeFormat:
    time_format = log_format.get("time", {})

    if not isinstance(time_format, dict):
        raise InvalidSettingsException(
            "A configuração 'format.time' deve ser um objeto."
        )

    enabled = _required_bool(time_format, "enabled")
    timezone = str(time_format.get("timezone", "UTC")).strip() or "UTC"
    precision_value = str(time_format.get("precision", "SECOND")).strip().upper()

    try:
        precision = TimePrecision(precision_value)
    except ValueError as error:
        raise InvalidSettingsException(
            f"Precisão de horário inválida: '{precision_value}'. "
            f"Valores suportados: {[item.value for item in TimePrecision]}"
        ) from error

    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as error:
        raise InvalidSettingsException(
            f"Fuso horário inválido ou indisponível: '{timezone}'."
        ) from error

    return LogTimeFormat(
        enabled=enabled,
        timezone=timezone,
        precision=precision,
    )


def _load_log_format(settings: dict) -> LogFormat:
    log_format = settings.get("format", settings.get("log_format", {}))

    if not isinstance(log_format, dict):
        raise InvalidSettingsException("A configuração 'format' deve ser um objeto.")

    app_name_format = log_format.get("app_name", {})
    source_format = log_format.get("source", {})

    if not isinstance(app_name_format, dict):
        raise InvalidSettingsException("A configuração 'format.app_name' deve ser um objeto.")

    if not isinstance(source_format, dict):
        raise InvalidSettingsException("A configuração 'format.source' deve ser um objeto.")

    return LogFormat(
        time=_load_time_format(log_format),
        app_name=AppNameFormat(
            enabled=_required_bool(app_name_format, "enabled"),
        ),
        source=SourceFormat(
            enabled=_required_bool(source_format, "enabled"),
            full_path=_required_bool(source_format, "full_path"),
        ),
    )

# =============================================================================

def load_settings():
    config_path = Path.cwd() / "logdock.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        settings = json.load(file)

        app_name = settings["app_name"]                                                 # Nome do app

        notification_enabled = settings["notification_enabled"]                           # Notificação habilitada | desabilitada
        notification_provider = settings["notification_provider"]                         # Provider de notificação 
        persistence_enabled = settings["persistence_enabled"] 
        persistence_provider = settings["persistence_provider"]

        log_level=str(settings["log_level"]).strip().upper() or "INFO"
        log_format = _load_log_format(settings)

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
                        endpoint=_required_env("LOGDOCK_AZURE_FUNCTION_ENDPOINT"),
                        function_key=_required_env("LOGDOCK_AZURE_FUNCTION_KEY"),
                        )

                case NotificationProvider.TELEGRAM:
                    notification = TelegramNotification(
                        enabled=True,
                        provider=NotificationProvider.TELEGRAM, 
                        token=_required_env("LOGDOCK_TELEGRAM_BOT_TOKEN"),
                        chat_id=_required_env("LOGDOCK_TELEGRAM_CHAT_ID"),
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
                        connection_string=_required_env(
                            "LOGDOCK_AZURE_BLOB_CONNECTION_STRING"
                        ),
                        container=_required_env("LOGDOCK_AZURE_BLOB_CONTAINER"),
                    )

        else:
            persistence = Persistence()    

        # =============================================================
        # region Level
        
        try:
            level = Levels(log_level)
        except ValueError:
            raise InvalidSettingsException(
                f"Level invalido: '{log_level}'. "
                f"Valores suportados: {[item.value for item in Levels]}"
            )
        
        # =============================================================
        # region Montar setting final
        logdock_settings = LogDockSettings(
            app_name=app_name,
            persistence=persistence,
            notification=notification,
            log_format=log_format,
            level=level
        )

        return logdock_settings
