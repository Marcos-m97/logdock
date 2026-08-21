import json
import logging
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

from ..config.loader import load_settings
from ..register.register import register_integrations
from ..config.settings import (
    NotificationProvider,
    PersistResult,
)
from ..config.loader import InvalidSettingsException
from .buffer import LogBufferHandler
from .formatter import LogDockFormatter


internal_logger = logging.getLogger("logdock.internal")

class LogDock:

    # region init 
    def __init__(self):
        self.logger = None
        self.execution_id = uuid4().hex[:12]
        self._buffer_handler = None
        self._persist_sequence = 0
        self.telegram_client = None
        self.persistence_client = None

        try:
            # Carrega configuraçõe
            self.logdock_settings = load_settings()

            integrations = register_integrations(logdock_settings=self.logdock_settings)

            # Carregar integrações
            self.telegram_client = integrations.telegram_client
            self.persistence_client = integrations.persistence_client

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

            if self.logdock_settings.persistence.enabled:
                self._buffer_handler = LogBufferHandler(
                    execution_id=self.execution_id,
                    log_format=self.logdock_settings.log_format,
                )
                self.logger.addHandler(self._buffer_handler)

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

            internal_logger.warning(
                "LogDock configuration failed. Basic mode enabled; "
                "persistence and notifications are disabled. Error: %s",
                error,
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
        self.logger.info(
            message,
            extra={"logdock_execution_id": self.execution_id},
            stacklevel=2,
        )
        if notify:
           self.notify(message)

    # ----------------------------------------
    def error(self, message, notify=False):
        self.logger.error(
            message,
            extra={"logdock_execution_id": self.execution_id},
            stacklevel=2,
        )
        if notify:
            self.notify(message)
        
    # ----------------------------------------
    def warning(self, message, notify=False):
        self.logger.warning(
            message,
            extra={"logdock_execution_id": self.execution_id},
            stacklevel=2,
        )
        if notify:
            self.notify(message)
            
    # ----------------------------------------
    # Só aparece o log de debug se o log_level for DEBUG (porém debug é nativo de logging, ver um outro nome para filtrar verbosisda)
    def debug(self, message, notify=False):
        self.logger.debug(
            message,
            extra={"logdock_execution_id": self.execution_id},
            stacklevel=2,
        )
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
            internal_logger.warning(
                "Notification requested while notifications are disabled."
            )
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
    def persist(self) -> PersistResult:
        """Persiste manualmente os registros acumulados nesta execução."""
        settings = getattr(self, "logdock_settings", None)
        persistence = getattr(settings, "persistence", None)
        if not persistence or not persistence.enabled:
            return PersistResult(
                success=False,
                provider=None,
                location=None,
                records_count=0,
                error="Persistência desabilitada.",
            )

        records = self._buffer_handler.snapshot()
        provider = persistence.provider.value
        if not records:
            return PersistResult(
                success=True,
                provider=provider,
                location=None,
                records_count=0,
            )

        persisted_datetime = datetime.now(
            ZoneInfo(self.logdock_settings.log_format.time.timezone)
        )
        execution = {
            "id": self.execution_id,
            "records_count": len(records),
        }
        if self.logdock_settings.log_format.app_name.enabled:
            execution["app_name"] = self.logdock_settings.app_name
        if self.logdock_settings.log_format.time.enabled:
            execution["persisted_at"] = LogDockFormatter(
                self.logdock_settings.log_format
            ).format_datetime(persisted_datetime)

        document = {
            "execution": execution,
            "logs": records,
        }
        content = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
        execution_date = persisted_datetime.date()
        safe_app_name = "".join(
            character if character.isalnum() or character in "-_" else "_"
            for character in self.logdock_settings.app_name
        )
        next_sequence = self._persist_sequence + 1
        file_name = (
            f"{self.execution_id}.json"
            if next_sequence == 1
            else f"{self.execution_id}-{next_sequence}.json"
        )
        object_name = str(
            Path(safe_app_name)
            / execution_date.isoformat()
            / file_name
        )

        try:
            if self.persistence_client is None:
                raise ValueError(f"Provider não implementado: {provider}")
            location = self.persistence_client.persist(content, object_name)
        except Exception as error:
            return PersistResult(
                success=False,
                provider=provider,
                location=None,
                records_count=len(records),
                error=f"{type(error).__name__}: {error}",
            )

        self._buffer_handler.discard(len(records))
        self._persist_sequence = next_sequence
        return PersistResult(
            success=True,
            provider=provider,
            location=location,
            records_count=len(records),
        )
    # endregion
