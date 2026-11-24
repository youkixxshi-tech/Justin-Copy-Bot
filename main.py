import os
import re
import logging
import requests
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Environment variable "BOT_TOKEN" ရှိရင် အဲဒါကို သုံးမယ်၊ မရှိရင် ဘေးက fallback token ကို သုံးမယ်
BOT_TOKEN = os.getenv("BOT_TOKEN") or "9159159164:AAE-nqw-jpjV9K8ZEwkuWc5RKENwH2A73Po"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_message(chat_id, text):
    if not API_URL:
        logger.warning("BOT_TOKEN is missing.")
        return

    response = requests.post(
        f"{API_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        },
        timeout=15
    )
    response.raise_for_status()


@app.route("/", methods=["GET"])
def home():
    return "MLBB ID Copy Bot is running!", 200


@app.route("/webhook/<secret>", methods=["POST"])
def webhook(secret):
    if not WEBHOOK_SECRET or secret != WEBHOOK_SECRET:
        abort(403)

    update = request.get_json(silent=True) or {}
    message = update.get("message", {})

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return jsonify(ok=True)

    if text.startswith("/start"):
        send_message(
            chat_id,
            "Welcome to MLBB ID Copy Bot!\n\n"
            "Send your MLBB ID and Server ID.\n\n"
            "Example: <code>123456789 (1234)</code>"
        )
        return jsonify(ok=True)

    if text.startswith("/help"):
        send_message(
            chat_id,
            "Send your ID like this:\n"
            "<code>123456789 (1234)</code>"
        )
        return jsonify(ok=True)

    match = re.fullmatch(
        r"(\d{1,20})\s*(?:\(\s*(\d{1,6})\s*\)|\s+(\d{1,6}))",
        text
    )

    if not match:
        send_message(
            chat_id,
            "Invalid format!\n\n"
            "Example: <code>123456789 (1234)</code>"
        )
        return jsonify(ok=True)

    player_id = match.group(1)
    server_id = match.group(2) or match.group(3)
    combined_id = player_id + server_id

    send_message(
        chat_id,
        f"Player ID: <code>{player_id}</code>\n"
        f"Server ID: <code>{server_id}</code>\n\n"
        f"Copy ID:\n<code>{combined_id}</code>"
    )

    return jsonify(ok=True)


def setup_webhook():
    if not all([API_URL, WEBHOOK_SECRET, RENDER_URL]):
        logger.warning("Webhook environment variables are missing.")
        return

    base_url = RENDER_URL.rstrip("/")
    url = f"{base_url}/webhook/{WEBHOOK_SECRET}"

    response = requests.post(
        f"{API_URL}/setWebhook",
        json={"url": url, "max_connections": 10},
        timeout=20
    )
    response.raise_for_status()
    logger.info("Webhook setup: %s", response.json())


setup_webhook()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
