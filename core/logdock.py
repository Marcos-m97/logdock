import logging
from ..config.loader import load_settings
from ..register.register import register_integrations
from ..config.settings import TelegramNotification, AzureFunctionNotification, NotificationProvider
from ..config.loader import InvalidSettingsException
from .formatter import LogDockFormatter

class LogDock:

    # region init 
    def __init__(self):
        self.logger = None

        try:
            # Carrega configuraçõe
            self.logdock_settings = load_settings()

            integrations = register_integrations(logdock_settings=self.logdock_settings)

            # Carregar integrações
            if integrations:
                self.telegram_client = integrations.telegram_client

            # print(f"DEBUG: {logdock_settings}")

            level = self.logdock_settings.level
            app_name = self.logdock_settings.app_name
           
            # Configura logging padrão
            logging.basicConfig(
                level=level,
            )

            formatter = LogDockFormatter(self.logdock_settings.log_format)
            for handler in logging.getLogger().handlers:
                handler.setFormatter(formatter)

            self.logger = logging.getLogger(app_name)
            
            self.logger.setLevel(level)

            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("requests").setLevel(logging.WARNING)

            # factory 

        except InvalidSettingsException:
            raise

        except Exception as error:

            logging.basicConfig(
                level=logging.INFO,
                format="%(levelname)s | %(message)s",
                # format="%(levelname)s | %(name)s | %(message)s",
            )

            self.logger = logging.getLogger("logdock")

            self.logger.warning(
                "Não foi possível configurar o LogDock. "
                "Modo básico ativado. "
                "Persistência e notificação desativadas. "
                f"Erro: {error}"
            )
    # ================================================================================
    # Adicionar hora, suporte para configurar fuso e nivel de hora em (secs, min, hora, dia, milisec etc) via configjson
    # Adicionar origem - apenas o arquivo de onde o log esta sendo emitido sem caminho raiz. 
    # Habilitar opção para ligar desligar o nome do app no log
    # Adicionar suporte para logs com quebra de linhas: ex uma lista onde cada item é uma linha.
    # Adicionar ordenação dinamica dos elementos do log através do logdock.json

    # region Métodos de log
    """
      Níveis de log têm uma hierarquia na lib padrão. Com level=logging.INFO, o logger mostra mensagens de INFO para cima:
            DEBUG    = 10  → oculto
            INFO     = 20  → exibido
            WARNING  = 30  → exibido
            ERROR    = 40  → exibido
            CRITICAL = 50  → exibido
    """

    def info(self, message, notify=False):
        self.logger.info(message, stacklevel=2)
        if notify:
           self.notify(message)

    # ----------------------------------------
    def error(self, message, notify=False):
        self.logger.error(message, stacklevel=2)
        if notify:
            self.notify(message)
        
    # ----------------------------------------
    def warning(self, message, notify=False):
        self.logger.warning(message, stacklevel=2)
        if notify:
            self.notify(message)
            
    # ----------------------------------------
    # Só aparece o log de debug se o log_level for DEBUG (porém debug é nativo de logging, ver um outro nome para filtrar verbosisda)
    def debug(self, message, notify=False):
        self.logger.debug(message, stacklevel=2)
        if notify:
            self.notify(message)
        
    # endregion

    # ================================================================================
    # region Notificação 
    def notify(
      self, 
      message : str = None
    ):
        """
        Roteador de noticações; 
        - Cada provider de notificação suportado deve ser chamado aqui 
        """

        # Validar se está eneabled se não estiver não deve funcionar mesmo que chamado
        is_enabled = self.logdock_settings.notification.enabled

        if not is_enabled:
            self.warning("Notificação solicitada porém esta desabilitada")
            return

        notification_provider = self.logdock_settings.notification.provider

        match notification_provider:

            case NotificationProvider.TELEGRAM:
                self.telegram_client.post_telegram_message(message)

            case NotificationProvider.AZURE_FUNCTION:
                pass

    # # endregion

    # ================================================================================
    # region Persistencia
    def persist(self):
        """
        Implemetar futuramente 
        """
        pass
    # endregion
