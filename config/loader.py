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
    LocalPersistence,
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
    enabled = _required_bool(log_format, "time_enabled")
    timezone = str(log_format.get("timezone", "UTC")).strip() or "UTC"
    precision_value = str(log_format.get("time_precision", "SECOND")).strip().upper()

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
    log_format = settings.get("format", {})

    if not isinstance(log_format, dict):
        raise InvalidSettingsException("A configuração 'format' deve ser um objeto.")

    return LogFormat(
        time=_load_time_format(log_format),
        app_name=AppNameFormat(
            enabled=_required_bool(log_format, "app_name_enabled"),
        ),
        source=SourceFormat(
            enabled=_required_bool(log_format, "source_enabled"),
            full_path=_required_bool(log_format, "source_full_path"),
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

        notification_settings = settings["notification"]
        persistence_settings = settings["persistence"]

        if not isinstance(notification_settings, dict):
            raise InvalidSettingsException(
                "A configuração 'notification' deve ser um objeto."
            )

        if not isinstance(persistence_settings, dict):
            raise InvalidSettingsException(
                "A configuração 'persistence' deve ser um objeto."
            )

        notification_enabled = _required_bool(notification_settings, "enabled")
        notification_provider = str(notification_settings.get("provider", "")).strip().upper()
        persistence_enabled = _required_bool(persistence_settings, "enabled")
        persistence_provider = (
            str(persistence_settings.get("provider", "LOCAL")).strip().upper()
            or "LOCAL"
        )

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
                    f"Persistence provider inválido: '{persistence_provider}'. "
                    f"Valores suportados: {[item.value for item in PersistenceProvider]}"
                )

            # Instanciar notification com base no provider identificado: 
            match persistence_provider:
                case PersistenceProvider.LOCAL:
                    local_path = str(persistence_settings.get("path", "./logs")).strip()
                    if not local_path:
                        raise InvalidSettingsException(
                            "O caminho da persistência local não pode ser vazio."
                        )
                    persistence = LocalPersistence(
                        enabled=True,
                        provider=PersistenceProvider.LOCAL,
                        path=local_path,
                    )

                case PersistenceProvider.AZURE_BLOB_STORAGE:
                    persistence = AzureBlobStoragePersistence(
                        enabled=True,
                        provider=PersistenceProvider.AZURE_BLOB_STORAGE,
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
