import logging
from config.loader import load_settings
from config. settings import TelegramNotification

class LogDock:

   
    # Adicionar suported persistence e notification (futuramente trasnformar em um factory ou register)

    def __init__(self):
        self.logger = None

        try:
            # Carrega configuraçõe
            self.logdock_settings = load_settings()

            # print(f"DEBUG: {logdock_settings}")

            # level_name = self.logdock_settings.level
            # notificaion_provider = self.logdock_settings.notification.provider
            # persistence_provider = self.logdock_settings.persistence.provider

            # # Validar configs, se config qualqur config invalida seta logger padrão: 
            # validate_suported(level_name, notificaion_provider, persistence_provider)

            level = self.logdock_settings.level
            app_name = self.logdock_settings.app_name
           
            # Configura logging padrão
            logging.basicConfig(
                level=level,
                format="%(levelname)s | %(message)s",
                # format="%(levelname)s | %(name)s | %(message)s",
            )

            self.logger = logging.getLogger(app_name)
            
            self.logger.setLevel(level)

            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("requests").setLevel(logging.WARNING)

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



    # region Métdos de log
    # Níveis têm uma hierarquia. Com level=logging.INFO, o logger mostra mensagens de INFO para cima:
        # DEBUG    = 10  → oculto
        # INFO     = 20  → exibido
        # WARNING  = 30  → exibido
        # ERROR    = 40  → exibido
        # CRITICAL = 50  → exibido
    
    def info(self, message, notify=False):
        self.logger.info(message)
        
    def error(self, message, notify=False):
        self.logger.error(message)

    def warning(self, message, notify=False):
        self.logger.warning(message)

    # Só aparece o log de debug se o log_level for DEBUG (porém debug é nativo de logging, ver um outro nome para filtrar verbosisda)
    def debug(self, message, notify=False):
        self.logger.debug(message) 
    
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

        # Validar se está enebled se não não deve funcionar mesmo que chamado
        is_enabled = self.logdock_settings.notification.enabled

        if not is_enabled:
            self.info("Notificação está desabilitado")
            return
        
        # Validar qual o tipo de provider com is_instance 
        provider = self.logdock_settings.notification

        # Telegram
        if isinstance(provider, TelegramNotification):
            pass
         

        # Whatsapp 
        
        # Azure function

        pass


    # endregion

    # ================================================================================
    # region Persistencia
    def persist(self):
        """
        Implemetar futuramente 
        """
        pass
    # endregion
