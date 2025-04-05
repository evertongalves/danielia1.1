from flask import Flask, request
import requests
from openai import OpenAI
import os

app = Flask(__name__)

# Pega as chaves do ambiente do Railway
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

# Cliente OpenAI atualizado
client = OpenAI(api_key=OPENAI_API_KEY)

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
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}]
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = f"Erro ao gerar resposta: {str(e)}"

        send_message(chat_id, reply)

    return {"ok": True}

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
