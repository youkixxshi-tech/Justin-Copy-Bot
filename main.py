import os
import re
import logging
import requests
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

BOT_TOKEN = os.getenv("9159159164:AAE-nqw-jpjV9K8ZEwkuWc5RKENwH2A73Po")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_message(chat_id, text):
    if not API_URL:
        return

    requests.post(
        f"{API_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        },
        timeout=15
    ).raise_for_status()


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
    text = message.get("text", "").strip()

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

    url = f"{RENDER_URL}/webhook/{WEBHOOK_SECRET}"

    response = requests.post(
        f"{API_URL}/setWebhook",
        json={"url": url, "max_connections": 10},
        timeout=20
    )
    response.raise_for_status()
    logger.info("Webhook setup: %s", response.json())


setup_webhook()
