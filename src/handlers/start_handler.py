import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.utils.validators import admin_only
from src.utils.keyboards import channel_selection_keyboard, channel_menu_keyboard, admin_panel_keyboard

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

WELCOME_MESSAGE = "🤖 به پنل مدیریت ربات خوش آمدید!\n\n📺 لطفاً کانال مورد نظر خود را انتخاب کنید:"

@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message and channel selection keyboard."""
    user = update.effective_user
    logger.info(f"Admin {user.id} ({user.username}) started the bot.")
    
    # پاک کردن کانال قبلی
    context.user_data.pop('selected_channel', None)
    
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=channel_selection_keyboard()
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
async def handle_channel_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles channel selection."""
    text = update.message.text
    
    if text == "🎬 کانال فیلم":
        context.user_data['selected_channel'] = 'film'
        context.user_data['channel_name'] = '🎬 کانال فیلم'
        await update.message.reply_text(
            f"✅ کانال فیلم انتخاب شد\n\nمنوی مدیریت:",
            reply_markup=channel_menu_keyboard('film')
        )
    elif text == "🇮🇹 کانال ایتالیا":
        context.user_data['selected_channel'] = 'italia'
        context.user_data['channel_name'] = '🇮🇹 کانال ایتالیا'
        await update.message.reply_text(
            f"✅ کانال ایتالیا انتخاب شد\n\nمنوی مدیریت:",
            reply_markup=channel_menu_keyboard('italia')
        )

@admin_only
async def handle_back_to_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles back to channel selection."""
    context.user_data.pop('selected_channel', None)
    context.user_data.pop('channel_name', None)
    
    await update.message.reply_text(
        "🔙 بازگشت به انتخاب کانال\n\n📺 لطفاً کانال مورد نظر خود را انتخاب کنید:",
        reply_markup=channel_selection_keyboard()
    )

@admin_only
async def handle_main_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles main menu button presses."""
    text = update.message.text
    
    if text == "⚙️ مدیریت انواع پست":
        selected_channel = context.user_data.get('channel_name', 'کانال')
        await update.message.reply_text(
            text=f"به پنل مدیریت {selected_channel} خوش آمدید.",
            reply_markup=admin_panel_keyboard()
        )
