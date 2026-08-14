# logdock/config.py

import json
from pathlib import Path
from .settings import LogDockSettings, Persistence, Notification, Levels


def load_settings():
    config_path = Path.cwd() / "logdock.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        settings = json.load(file)

        app_name = settings["app_name"]

        persistence_enabled= settings["persistence_enabled"] 
        persistence_provider=settings["persistence_provider"] 
        persistence_connection_string=settings["persistence_connection_string"] 
        persistence_container=settings["persistence_container"] 

        notification_enabled=settings["notification_enabled"] 
        notification_provider=settings["notification_provider"] 
        notification_chat_id=settings["notification_chat_id"] 

        log_level=str(settings["log_level"]).strip().upper() or "INFO"

        # =============================================================
        # region Notificação 
        notification = Notification(
            enabled=notification_enabled,
            provider=notification_provider,
            chat_id=notification_chat_id
        )

        # =============================================================
        # region Persistencia
        persistence = Persistence(
            enabled=persistence_enabled,
            provider=persistence_provider,
            connection_string=persistence_connection_string,
            container=persistence_container
        )

        # =============================================================
        # region Level do log 
        level = Levels(log_level)

        # =============================================================
        # region Montar setting final
        logdock_settings = LogDockSettings(
            app_name=app_name,
            persistence=persistence,
            notification=notification,
            level=level
        )

        return logdock_settings