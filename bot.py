import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo, BotCommand
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

WEBAPP_URL = "https://natnael-code.github.io/telegram-route-app/index.html"

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

async def post_init(application: Application) -> None:
    """Registers the /start command in Telegram's menu button."""
    commands = [
        BotCommand("start", "📍 Show Navigation Buttons")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands successfully registered with Telegram.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Persistent Reply Keyboard attached to the bottom of the chat window
        keyboard = [
            [
                KeyboardButton(
                    "📍 Church (Live GPS)", 
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}?dest=church&start=gps")
                )
            ],
            [
                KeyboardButton(
                    "📍 Church (From Uni Gate [Toni])", 
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}?dest=church&start=uni")
                )
            ],
            [
                KeyboardButton(
                    "⛪ Chapel (Live GPS)", 
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}?dest=chapel&start=gps")
                )
            ],
            [
                KeyboardButton(
                    "⛪ Chapel (From Uni Gate [Toni])", 
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}?dest=chapel&start=uni")
                )
            ]
        ]
        
        # resize_keyboard=True keeps the buttons compact at the bottom
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        welcome_text = (
            "Welcome to the Fellowship Navigation Bot! ⛪\n\n"
            "Your navigation buttons are now locked at the bottom of your screen.\n\n"
            "ማለዳ ጸሎት ከሰኞ እስከ ቅዳሜ በ chapel\n"
            "general fellow ቅዳሜ ከ12:00 ሰአት ጀምሮ በ ምእራብ መሰረተ ክርስቶስ"
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("Unable to load navigation options. Please try again.")

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

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request)
        .post_init(post_init)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_error_handler(error_handler)
    
    logger.info("Bot is active...")
    app.run_polling(
        poll_interval=1.0,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()