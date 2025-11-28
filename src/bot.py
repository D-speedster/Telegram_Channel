import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Import handlers
from src.handlers.start_handler import (
    start as start_admin, 
    back_to_main_menu
)
from src.handlers.ai_post_handler import ai_post_handler
from src.handlers.post_handler import post_creation_handler
from src.handlers.admin_handlers import admin_management_handler, admin_panel
from src.handlers.movie_design_handler import movie_design_handler

# Import configuration
from src.config import TELEGRAM_BOT_TOKEN, LOG_LEVEL

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL, logging.INFO)
)
logger = logging.getLogger(__name__)

# --- Error Handler ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    # Optionally, notify the user or developer
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("متاسفانه خطایی رخ داده است. لطفا دوباره تلاش کنید.")
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")

# --- Main Bot Logic ---
def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # --- Register Handlers ---
    # Add command handlers first
    application.add_handler(CommandHandler("start", start_admin))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # Add conversation handlers
    application.add_handler(ai_post_handler)  # ساخت پست هوشمند
    application.add_handler(movie_design_handler)  # پست فیلم
    application.add_handler(post_creation_handler)
    application.add_handler(admin_management_handler)

    # Add callback query handlers
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main_menu$'))

    # Register the error handler
    application.add_error_handler(error_handler)

    # Run the bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
