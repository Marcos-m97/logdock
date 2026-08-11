import logging
from config.loader import load_config
from config.settings import LogDockSettings, Levels, Persistence, Notification

# class LogDock:

#     def __init__(self):

#         # No lugar de passar esses dados no init talvez criar a obrigagoriedade
#         # um loc_dock.json para carregar todas as configs.
#         try:

#             # Carregar configurações do json logdock_json da aplicação.
#             config = load_config()

#             app_name = config["app_name"]
#             persistence_enabled = config["persistence_enabled"]
#             persistence_provider = config["persistence_provider"]
#             persistence_connection_string = config["persistence_connection_string"]
#             persistence_container = config["persistence_container"]
#             notification_enabled = config["notification_enabled"]
#             notification_provider = config["notification_provider"]
#             notification_chat_id = config["notification_chat_id"]
#             log_level = config["log_level"]


#             # factory de features da lib 
#             persistence = Persistence(
#                 enabled=persistence_enabled,
#                 provider=persistence_provider,
#                 connection_string=persistence_connection_string,
#                 container=persistence_container
#             )

#             notification = Notification(
#                 enabled=notification_enabled,
#                 provider=notification_provider,
#                 chat_id=notification_chat_id,
#             )

#             # container de settings
#             logdock_settings = LogDockSettings(
#                 app_name = app_name,
#                 persistence = persistence,
#                 notification= notification,
#                 level=log_level
#             )

#             # Configura loger padrão
#             level_name = str(logdock_settings.level or "INFO").strip().upper()
#             level = getattr(logging, level_name, logging.INFO)

#             logging.basicConfig(
#                 level=level,
#                 format="%(levelname)s | %(name)s | %(message)s",
#             )

#             logging.getLogger().setLevel(level)

#             # Restringe logs de libs cadastradas. (evoluir futuramente)
#             logging.getLogger("urllib3").setLevel(logging.WARNING)
#             logging.getLogger("requests").setLevel(logging.WARNING)
        
#         except Exception as error:
#             error_message = f"Não foi possível configurar o logdock, Modo básico ativado (Notificação e Persistencia desativados) | Erro: {error}"
#             #configurar logger padrão que functione com o mesma chamada logger

#     # ================================================================================
#     def notify(
#         self, 
#         send: bool = False, 
#         message : str = None
#         ):

#         """
#         Envia notificação pra um canal de comunicação (realiza o request). (Seja erro ou outros)
#         implementar futuramente
#         """
#         pass


#     # Implemetar método para logger usar 

#     def send_log_file(self):
#         """
#         Envia um arquivo de log para um canal de comunicação
#         Implementar futuramente 
#         """
#         pass


#     def persist_log(self):
#         """
#         Implemetar futuramente 
#         """
#         pass


# ==================
class LogDock:
    def __init__(self):
        self.logger = None

        try:
            config = load_config()

            persistence = Persistence(
                enabled=config["persistence_enabled"],
                provider=config["persistence_provider"],
                connection_string=config["persistence_connection_string"],
                container=config["persistence_container"],
            )

            notification = Notification(
                enabled=config["notification_enabled"],
                provider=config["notification_provider"],
                chat_id=config["notification_chat_id"],
            )

            settings = LogDockSettings(
                app_name=config["app_name"],
                persistence=persistence,
                notification=notification,
                level=config["log_level"],
            )

            level_name = str(settings.level or "INFO").strip().upper()

            level = getattr(
                logging,
                level_name,
                logging.INFO
            )

            logging.basicConfig(
                level=level,
                format="%(levelname)s | %(name)s | %(message)s",
            )

            self.logger = logging.getLogger(
                settings.app_name
            )

            self.logger.setLevel(level)

            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("requests").setLevel(logging.WARNING)

        except Exception as error:

            logging.basicConfig(
                level=logging.INFO,
                format="%(levelname)s | %(name)s | %(message)s",
            )

            self.logger = logging.getLogger("logdock")

            self.logger.warning(
                "Não foi possível configurar o LogDock. "
                "Modo básico ativado. "
                "Persistência e notificação desativadas. "
                f"Erro: {error}"
            )