from ..integrations.telegram_client import TelegramClient
from ..config.settings import LogDockSettings, LogDockIntegrations, TelegramNotification, AzureFunctionNotification

def register_integrations(logdock_settings: LogDockSettings):
  
    notification_enabled = logdock_settings.notification.enabled

    if notification_enabled:
    # Validar qual o tipo de provider com isinstance
        
        # A propriedade 'notification' de logdock_settings recebe a dataclass do provider selecionado
        notification_provider = logdock_settings.notification

        # ----------------------------------------------------------------------------    
        # Telegram
        if isinstance(notification_provider, TelegramNotification):
            # print("DEV DEBUG - NOTIFICAÇÃO VIA TELEGRAM")
            # endpoint = provider.endpoint
            token = notification_provider.token
            chat_id = notification_provider.chat_id

            # Instancia o client do telegram
            telegram_client = TelegramClient(
                token=token,
                chat_id=chat_id 
            )

        # ----------------------------------------------------------------------------    
        # Azurefunction
        if isinstance(notification_provider, AzureFunctionNotification):
            # print("DEV DEBUG - NOTIFICAÇÃO VIA AZURE FUNCTION")
            endpoint = notification_provider.endpoint
            # send_message_azurefunction()

            # az_function_client()

        # ----------------------------------------------------------------------------
        # Build final 
        logdock_integrations = LogDockIntegrations(
            telegram_client=telegram_client
        )

        return logdock_integrations

