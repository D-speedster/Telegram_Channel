import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.utils.validators import admin_only
from src.utils.keyboards import main_menu_keyboard, admin_panel_keyboard

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

WELCOME_MESSAGE = "🤖 به پنل مدیریت ربات خوش آمدید!\n\nاز طریق منوی زیر می‌توانید اقدام کنید:"

@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message and the main menu keyboard when the /start command is issued by an admin."""
    user = update.effective_user
    logger.info(f"Admin {user.id} ({user.username}) started the bot.")
    
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=main_menu_keyboard()
    )

@admin_only
async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the 'back_to_main_menu' callback, sending the main menu."""
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Admin {query.from_user.id} returned to the main menu.")
    
    await query.edit_message_text(text="🔙 بازگشت به منوی اصلی")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="منوی اصلی:",
        reply_markup=main_menu_keyboard()
    )

@admin_only
async def handle_main_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles main menu button presses."""
    text = update.message.text
    
    if text == "⚙️ مدیریت انواع پست":
        await update.message.reply_text(
            text="به پنل مدیریت خوش آمدید.",
            reply_markup=admin_panel_keyboard()
        )
    elif text == "📊 آمار و گزارش":
        await update.message.reply_text(
            text="این بخش در حال توسعه است.",
            reply_markup=main_menu_keyboard()
        )
