import logging
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

# Configure logging to catch network issues cleanly
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN is missing. Please set it in your .env file.")

WEBAPP_URL = "https://natnael-code.github.io/telegram-route-app"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "📍 Church (From My Live GPS Location)", 
                web_app={"url": f"{WEBAPP_URL}?dest=church&start=gps"}
            )
        ],
        [
            InlineKeyboardButton(
                "📍 Church (From University Gate)", 
                web_app={"url": f"{WEBAPP_URL}?dest=church&start=uni"}
            )
        ],
        [
            InlineKeyboardButton(
                "🏠 Chapel (From My Live GPS Location)", 
                web_app={"url": f"{WEBAPP_URL}?dest=gathering&start=gps"}
            )
        ],
        [
            InlineKeyboardButton(
                "🏠 Chapel (From University Gate)", 
                web_app={"url": f"{WEBAPP_URL}?dest=gathering&start=uni"}
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to the Fellowship Navigation Bot! ⛪\n\nChoose your starting point and destination:",
        reply_markup=reply_markup
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log network and execution errors without crashing the main process loop."""
    logger.error("Exception while handling an update:", exc_info=context.error)

def main():
    # Configure HTTP client timeouts for weak or high-latency connections
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )

    app = Application.builder().token(BOT_TOKEN).request(request).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_error_handler(error_handler)
    
    print("Bot is starting...")
    
    # Run polling loop with connection resilience
    app.run_polling(poll_interval=1.0)

if __name__ == "__main__":
    main()