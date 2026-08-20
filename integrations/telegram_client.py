import logging

import requests


logger = logging.getLogger("logdock.internal")


class TelegramClient:
    def __init__(self, token: str, chat_id: str):
    
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def post_telegram_message(self, message: str) -> int | None:
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.debug(
                "Mensagem enviada ao Telegram. Status: %s",
                response.status_code,
            )
            return response.status_code

        except requests.exceptions.Timeout:
            logger.warning("Timeout ao enviar mensagem ao Telegram.")

        except requests.exceptions.ConnectionError:
            logger.warning("Erro de conexão ao enviar mensagem ao Telegram.")

        except requests.exceptions.HTTPError as error:
            status_code = (
                error.response.status_code
                if error.response is not None
                else "desconhecido"
            )
            logger.warning(
                "Erro HTTP ao enviar mensagem ao Telegram. Status: %s",
                status_code,
            )

        except requests.exceptions.RequestException as error:
            logger.warning(
                "Erro inesperado na requisição ao Telegram: %s.",
                type(error).__name__,
            )

        return None
