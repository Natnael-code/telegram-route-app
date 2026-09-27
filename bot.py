import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN missing in .env file.")

WEBAPP_URL = "https://natnael-code.github.io/telegram-route-app"

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return

def start_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Health check running on port {port}")
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Inline buttons utilizing WebAppInfo class required by Telegram SDK
    keyboard = [
        [
            InlineKeyboardButton(
                "📍 West MKC Church (Live GPS)", 
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?dest=church&start=gps")
            )
        ],
        [
            InlineKeyboardButton(
                "📍 West MKC Church (From University Gate [Toni])", 
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?dest=church&start=uni")
            )
        ],
        [
            InlineKeyboardButton(
                "⛪ Chapel (Live GPS)", 
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?dest=chapel&start=gps")
            )
        ],
        [
            InlineKeyboardButton(
                "⛪ Chapel (From University Gate [Toni])", 
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?dest=chapel&start=uni")
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to the Fellowship Navigation Bot! ⛪\n\nSelect your starting point and destination below:",
        reply_markup=reply_markup
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Error occurred:", exc_info=context.error)

def main():
    threading.Thread(target=start_health_check_server, daemon=True).start()

    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )

    app = Application.builder().token(BOT_TOKEN).request(request).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_error_handler(error_handler)
    
    logger.info("Bot is active...")
    app.run_polling(poll_interval=1.0)

if __name__ == "__main__":
    main()