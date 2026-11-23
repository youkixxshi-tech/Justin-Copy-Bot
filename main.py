
import os
import re
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("9159159164:AAE-nqw-jpjV9K8ZEwkuWc5RKENwH2A73Po")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to MLBB ID Copy Bot!\n\n"
        "Send your MLBB ID and Server ID.\n\n"
        "Example: 123456789 (1234)"
    )

async def copy_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    match = re.fullmatch(r"(\d+)\s*\(?\s*(\d{1,5})\s*\)?", text)

    if not match:
        await update.message.reply_text(
            "Invalid format!\n"
            "Example: 123456789 (1234)"
        )
        return

    player_id, server_id = match.groups()
    combined_id = player_id + server_id

    await update.message.reply_text(
        f"Player ID: <code>{player_id}</code>\n"
        f"Server ID: <code>{server_id}</code>\n\n"
        f"Copy ID:\n<code>{combined_id}</code>",
        parse_mode="HTML"
    )

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, copy_id))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
  
