from flask import Flask, request
import requests
import os
import openai  # Usaremos a biblioteca openai, porque DeepSeek segue o mesmo padrão!

app = Flask(__name__)

# Variáveis de ambiente
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

# Configuração do cliente DeepSeek (usa a lib openai, com base_url deles!)
client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1",
)

def send_message(chat_id, text):
    url = TELEGRAM_API_URL + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": user_message}]
            )
            reply = response.choices[0].message.content.strip()

        except openai.RateLimitError:
            reply = "Atenção! Limite de uso da DeepSeek atingido."
        except openai.APIError as e:
            reply = f"Erro na API DeepSeek: {str(e)}"
        except openai.APIConnectionError:
            reply = "Erro de conexão com a DeepSeek."
        except Exception as e:
            reply = f"Erro inesperado: {str(e)}"

        send_message(chat_id, reply)

    return {"ok": True}

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
