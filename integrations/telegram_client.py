import requests

class TelegramClient:
    def __init__(self, token: str, chat_id: str):
    
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def post_telegram_message(self, message):
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            resp = requests.post(self.base_url, json=payload, timeout=10)
            resp.raise_for_status()

            print(f"[OK] Mensagem enviada – código {resp.status_code}")
            return resp.status_code

        except requests.exceptions.HTTPError as e:
            print(f"[ERRO HTTP] {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"[ERRO DE CONEXÃO] {e}")
        except requests.exceptions.Timeout:
            print("[ERRO] Timeout na requisição")
        except Exception as e:
            print(f"[ERRO GERAL] {e}")

        return {}