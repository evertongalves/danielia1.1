from flask import Flask, request
import requests
import os
import groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Variáveis de ambiente
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

# Configuração do cliente Groq
client = groq.Groq(api_key=GROQ_API_KEY)

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
                model="llama3-8b-8192",  # modelo atualizado
                messages=[{"role": "user", "content": user_message}]
            )
            reply = response.choices[0].message.content.strip()

        except groq.APIError as e:
            reply = f"Erro na API Groq: {str(e)}"
        except groq.APIConnectionError:
            reply = "Erro de conexão com a Groq."
        except Exception as e:
            reply = f"Erro inesperado: {str(e)}"

        send_message(chat_id, reply)

    return {"ok": True}

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
