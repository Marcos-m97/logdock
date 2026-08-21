import logging

import requests


internal_logger = logging.getLogger("logdock.internal")


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

            internal_logger.debug(
                "Telegram message sent successfully. Status: %s",
                response.status_code,
            )
            return response.status_code

        except requests.exceptions.Timeout:
            internal_logger.warning("Telegram request timed out.")

        except requests.exceptions.ConnectionError:
            internal_logger.warning(
                "Connection error while sending a Telegram message."
            )

        except requests.exceptions.HTTPError as error:
            status_code = (
                error.response.status_code
                if error.response is not None
                else "desconhecido"
            )
            internal_logger.warning(
                "Telegram request failed with HTTP status %s.",
                status_code,
            )

        except requests.exceptions.RequestException as error:
            internal_logger.warning(
                "Unexpected Telegram request error: %s.",
                type(error).__name__,
            )

        return None
