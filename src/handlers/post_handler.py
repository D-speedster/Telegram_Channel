import logging
import os
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from src.config import CHANNEL_ID
from src.utils.validators import admin_only
from src.utils.keyboards import post_types_keyboard, confirm_keyboard, main_menu_keyboard
from src.utils.post_builder import send_post_to_channel
from src.database.database import DBManager

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Conversation States ---
SELECTING_POST_TYPE, WAITING_FOR_TEXT, WAITING_FOR_CONFIRM = range(3)

# --- Helper Functions ---
def create_preview(post_type: str, text: str, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    """
    Finds the banner for the post type and creates the preview text.
    Returns a tuple of (banner_path, preview_text).
    """
    banner_path = f"data/banners/{post_type}.jpg"
    if not os.path.exists(banner_path):
        banner_path = None
    context.user_data['banner_path'] = banner_path
    return banner_path, text

# --- Handler Functions ---

@admin_only
async def new_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the post creation process by showing post type options."""
    db = DBManager()
    try:
        post_types = [pt.name for pt in db.get_post_types()]
    finally:
        db.close()
    
    if not post_types:
        await update.message.reply_text(
            "هیچ نوع پستی تعریف نشده است. لطفاً ابتدا از پنل مدیریت نوع پست اضافه کنید.",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END
    
    logger.info(f"Admin {update.effective_user.id} started creating a new post.")

    await update.message.reply_text(
        text="لطفاً نوع پست خود را انتخاب کنید:",
        reply_markup=post_types_keyboard(post_types)
    )
    return SELECTING_POST_TYPE

@admin_only
async def post_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the selection of a post type and asks for the post text."""
    query = update.callback_query
    await query.answer()

    post_type = query.data.replace("post_type_", "")
    context.user_data['post_type'] = post_type
    
    logger.info(f"Admin {query.from_user.id} selected post type: {post_type}")

    await query.edit_message_text(
        text=f"شما نوع '{post_type}' را انتخاب کردید.\n\nاکنون، لطفاً متن پست را ارسال کنید:"
    )
    return WAITING_FOR_TEXT

@admin_only
async def text_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receives the post text, shows a preview with a banner, and asks for confirmation.
    """
    user_text = update.message.text
    context.user_data['text'] = user_text
    post_type = context.user_data.get('post_type')

    logger.info(f"Admin {update.effective_user.id} submitted text for '{post_type}' post.")

    banner_path, preview_text = create_preview(post_type, user_text, context)

    if banner_path:
        try:
            with open(banner_path, 'rb') as banner_file:
                await update.message.reply_photo(
                    photo=banner_file,
                    caption=f"پیش‌نمایش پست:\n\n{preview_text}",
                    reply_markup=confirm_keyboard()
                )
        except Exception as e:
            logger.error(f"Error sending photo banner: {e}")
            await update.message.reply_text(
                text=f"خطا در بارگذاری بنر. پیش‌نمایش بدون بنر:\n\n{preview_text}",
                reply_markup=confirm_keyboard()
            )
    else:
        await update.message.reply_text(
            text=f"بنری برای این نوع پست یافت نشد. پیش‌نمایش:\n\n{preview_text}",
            reply_markup=confirm_keyboard()
        )

    return WAITING_FOR_CONFIRM

@admin_only
async def confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's confirmation to send the post to the channel."""
    query = update.callback_query
    await query.answer()
    
    user_choice = query.data

    if user_choice == 'confirm_send':
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="در حال ارسال پست به کانال...")

        post_type = context.user_data.get('post_type')
        text = context.user_data.get('text')
        banner_path = context.user_data.get('banner_path')
        user_id = query.from_user.id

        success = await send_post_to_channel(context.bot, CHANNEL_ID, banner_path, text)

        if success:
            db = DBManager()
            try:
                db.add_post_log(post_type, text, user_id, banner_path)
            finally:
                db.close()
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="✅ پست با موفقیت به کانال ارسال شد.",
                reply_markup=main_menu_keyboard()
            )
            logger.info(f"Admin {user_id} successfully sent a '{post_type}' post to channel {CHANNEL_ID}.")
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="❌ خطایی در ارسال پست به کانال رخ داد. لطفاً دوباره تلاش کنید.",
                reply_markup=main_menu_keyboard()
            )
            logger.error(f"Failed to send post for admin {user_id} to channel {CHANNEL_ID}.")

        context.user_data.clear()
        return ConversationHandler.END

    elif user_choice == 'cancel_action':
        return await cancel(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    query = update.callback_query
    if query:
        await query.answer()
        logger.info(f"User {query.from_user.id} canceled the conversation.")
        await query.edit_message_text(text="❌ عملیات لغو شد.")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="به منوی اصلی بازگشتید:",
            reply_markup=main_menu_keyboard()
        )
    else:
        logger.info(f"User {update.effective_user.id} canceled the conversation.")
        await update.message.reply_text(
            "❌ عملیات لغو شد.",
            reply_markup=main_menu_keyboard()
        )
    
    context.user_data.clear()
    return ConversationHandler.END


# --- Conversation Handler ---
post_creation_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('^➕ ساخت پست جدید$'), new_post)],
    states={
        SELECTING_POST_TYPE: [
            CallbackQueryHandler(post_type_selected, pattern='^post_type_'),
            CallbackQueryHandler(cancel, pattern='^cancel_action$')
        ],
        WAITING_FOR_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, text_received)
        ],
        WAITING_FOR_CONFIRM: [
            CallbackQueryHandler(confirmation_handler, pattern='^(confirm_send|cancel_action)$')
        ]
    },
    fallbacks=[
        CallbackQueryHandler(cancel, pattern='^cancel_action$'),
        MessageHandler(filters.Regex('^❌ لغو$'), cancel)
    ],
    allow_reentry=True,
    per_message=False
)
